#!/usr/bin/env python3
"""
Email sender module for the lead generator.
"""

import smtplib
import time
import logging
import logging.handlers
import os.path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from contextlib import contextmanager

from ..config.email_config import (
    SMTP_CONFIG,
    EMAIL_TEMPLATES,
    EMAIL_VALIDATION,
    EMAIL_LOGGING
)

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(
    EMAIL_LOGGING['log_file'],
    maxBytes=EMAIL_LOGGING['max_file_size'],
    backupCount=EMAIL_LOGGING['backup_count']
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class EmailSender:
    """Handles email sending with rate limiting and batch processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email sender.
        
        Args:
            config: Optional configuration override
        """
        self.config = config or SMTP_CONFIG
        self.smtp = None
        self.last_sent_time = datetime.min
        self.sent_count = 0
        self._connect()
        
    def _connect(self) -> None:
        """Establish SMTP connection."""
        try:
            self.smtp = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            self.smtp.starttls()
            self.smtp.login(self.config['username'], self.config['password'])
            logger.info("SMTP connection established")
        except Exception as e:
            logger.error(f"Failed to establish SMTP connection: {str(e)}")
            raise
            
    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        now = datetime.now()
        if (now - self.last_sent_time) < timedelta(hours=1):
            if self.sent_count >= self.config['rate_limit']:
                wait_time = 3600 - (now - self.last_sent_time).seconds
                logger.info(f"Rate limit reached. Waiting {wait_time} seconds")
                time.sleep(wait_time)
                self.sent_count = 0
                self.last_sent_time = datetime.now()
        else:
            self.sent_count = 0
            self.last_sent_time = now
            
    def _create_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_paths: Optional[Union[str, List[str]]] = None,
        template: Optional[str] = None,
        **kwargs
    ) -> MIMEMultipart:
        """
        Create an email message, optionally with attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            attachment_paths: Path(s) to file(s) to attach (single string or list of strings)
            template: Optional template name
            **kwargs: Template variables
            
        Returns:
            MIMEMultipart message
        """
        msg = MIMEMultipart()
        msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if template:
            template_text = EMAIL_TEMPLATES.get(template, body)
            body = template_text.format(
                sender_name=self.config['from_name'],
                **kwargs
            )
            
        msg.attach(MIMEText(body, 'plain'))
        
        # Handle attachments
        if attachment_paths:
            # Convert single path to list
            if isinstance(attachment_paths, str):
                attachment_paths = [attachment_paths]
                
            for attachment_path in attachment_paths:
                try:
                    # Check if file exists
                    if not os.path.isfile(attachment_path):
                        logger.warning(f"Attachment file not found: {attachment_path}")
                        continue
                        
                    # Check file size
                    file_size = os.path.getsize(attachment_path)
                    if file_size > EMAIL_VALIDATION['max_attachment_size']:
                        logger.warning(f"Attachment exceeds size limit ({file_size} bytes): {attachment_path}")
                        continue
                    
                    # Get file name from path
                    filename = os.path.basename(attachment_path)
                    
                    # Read file and attach
                    with open(attachment_path, 'rb') as f:
                        attachment = MIMEApplication(f.read(), _subtype="pdf")
                        
                    # Add header with filename
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(attachment)
                    logger.info(f"Attached file: {filename} ({file_size} bytes)")
                    
                except Exception as e:
                    logger.error(f"Failed to attach file {attachment_path}: {str(e)}")
        
        return msg
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_paths: Optional[Union[str, List[str]]] = None,
        template: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Send a single email, optionally with attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            attachment_paths: Path(s) to file(s) to attach (single string or list of strings)
            template: Optional template name
            **kwargs: Template variables
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            self._check_rate_limit()
            msg = self._create_message(to_email, subject, body, attachment_paths, template, **kwargs)
            self.smtp.send_message(msg)
            self.sent_count += 1
            
            # Log with attachment info
            attachment_info = ""
            if attachment_paths:
                if isinstance(attachment_paths, str):
                    attachment_info = f" with attachment: {os.path.basename(attachment_paths)}"
                else:
                    attachment_info = f" with {len(attachment_paths)} attachments"
                    
            logger.info(f"Email sent successfully to {to_email}{attachment_info}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
            
    def send_batch(
        self,
        emails: List[Dict[str, Any]],
        max_retries: int = EMAIL_VALIDATION['max_retries']
    ) -> Dict[str, int]:
        """
        Send a batch of emails.
        
        Args:
            emails: List of email dictionaries with required fields
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with success and failure counts
        """
        results = {'success': 0, 'failure': 0}
        
        for email in emails:
            retries = 0
            while retries < max_retries:
                if self.send_email(**email):
                    results['success'] += 1
                    break
                retries += 1
                if retries < max_retries:
                    time.sleep(EMAIL_VALIDATION['retry_delay'])
            else:
                results['failure'] += 1
                
        return results
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.smtp:
            self.smtp.quit()
            logger.info("SMTP connection closed")
            
@contextmanager
def email_sender(config: Optional[Dict[str, Any]] = None):
    """
    Context manager for email sender.
    
    Args:
        config: Optional configuration override
        
    Yields:
        EmailSender instance
    """
    sender = EmailSender(config)
    try:
        yield sender
    finally:
        if sender.smtp:
            sender.smtp.quit()
            logger.info("SMTP connection closed") 