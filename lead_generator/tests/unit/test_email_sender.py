#!/usr/bin/env python3
"""
Test suite for the email sender module.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import time
from datetime import datetime, timedelta
from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from lead_generator.agents.email_sender import EmailSender, email_sender
from lead_generator.config.email_config import SMTP_CONFIG, EMAIL_TEMPLATES, EMAIL_VALIDATION

class TestEmailSender(unittest.TestCase):
    """Test cases for the EmailSender class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create patches for external dependencies
        self.smtp_patcher = patch('smtplib.SMTP')
        self.time_patcher = patch('time.sleep')
        
        # Start the patches
        self.mock_smtp = self.smtp_patcher.start()
        self.mock_time = self.time_patcher.start()
        
        # Set up mock SMTP instance
        self.mock_smtp_instance = MagicMock()
        self.mock_smtp.return_value = self.mock_smtp_instance
        
        # Test configuration
        self.test_config = {
            'smtp_server': 'test.example.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'test_password',
            'from_email': 'sender@example.com',
            'from_name': 'Test Sender',
            'rate_limit': 10,
            'batch_size': 5
        }
        
        # Initialize the EmailSender with test config
        self.sender = EmailSender(self.test_config)
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Stop the patches
        self.smtp_patcher.stop()
        self.time_patcher.stop()
    
    def test_initialization(self):
        """Test EmailSender initialization and connection."""
        # Verify the config was set correctly
        self.assertEqual(self.sender.config, self.test_config)
        
        # Verify SMTP connection was established
        self.mock_smtp.assert_called_once_with(
            self.test_config['smtp_server'],
            self.test_config['smtp_port']
        )
        self.mock_smtp_instance.starttls.assert_called_once()
        self.mock_smtp_instance.login.assert_called_once_with(
            self.test_config['username'],
            self.test_config['password']
        )
        
        # Test initialization with default config
        with patch('lead_generator.agents.email_sender.SMTP_CONFIG', self.test_config):
            sender = EmailSender()
            self.assertEqual(sender.config, self.test_config)
    
    def test_initialization_error(self):
        """Test error handling during initialization."""
        # Reset the mock to raise an exception
        self.mock_smtp.reset_mock()
        self.mock_smtp_instance.login.side_effect = Exception("Login failed")
        
        # Test that the exception is propagated
        with self.assertRaises(Exception):
            EmailSender(self.test_config)
    
    def test_create_message(self):
        """Test email message creation."""
        # Test basic message creation
        msg = self.sender._create_message(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertIsInstance(msg, MIMEMultipart)
        self.assertEqual(msg['Subject'], "Test Subject")
        self.assertEqual(msg['To'], "recipient@example.com")
        self.assertEqual(msg['From'], f"{self.test_config['from_name']} <{self.test_config['from_email']}>")
        
        # Test with template
        with patch('lead_generator.agents.email_sender.EMAIL_TEMPLATES', {
            'test_template': "Hello {name}, from {sender_name}"
        }):
            msg = self.sender._create_message(
                to_email="recipient@example.com",
                subject="Template Test",
                body="Fallback Body",
                template="test_template",
                name="John"
            )
            
            # Get the body content
            body_parts = [part.get_payload() for part in msg.get_payload()]
            self.assertIn("Hello John, from Test Sender", body_parts[0])
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Set up the sender for testing rate limits
        self.sender.sent_count = self.test_config['rate_limit']
        self.sender.last_sent_time = datetime.now() - timedelta(minutes=30)
        
        # Send an email, which should trigger rate limiting
        self.sender.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        # Verify that sleep was called with the expected wait time
        self.mock_time.assert_called_once()
        wait_args = self.mock_time.call_args[0][0]
        self.assertTrue(0 <= wait_args <= 3600)  # Should be positive and less than an hour
        
        # Test resetting the counter when an hour has passed
        self.sender.sent_count = 5
        self.sender.last_sent_time = datetime.now() - timedelta(hours=2)
        
        self.sender._check_rate_limit()
        self.assertEqual(self.sender.sent_count, 0)
    
    def test_send_email_success(self):
        """Test successful email sending."""
        # Test sending a basic email
        result = self.sender.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertTrue(result)
        self.mock_smtp_instance.send_message.assert_called_once()
        self.assertEqual(self.sender.sent_count, 1)
    
    def test_send_email_failure(self):
        """Test handling of email sending failures."""
        # Set up the mock to simulate a failure
        self.mock_smtp_instance.send_message.side_effect = Exception("Send failed")
        
        # Attempt to send an email
        result = self.sender.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertFalse(result)
        self.mock_smtp_instance.send_message.assert_called_once()
        self.assertEqual(self.sender.sent_count, 0)
    
    def test_send_batch(self):
        """Test sending a batch of emails."""
        # Prepare test data
        emails = [
            {
                "to_email": f"recipient{i}@example.com",
                "subject": f"Test Subject {i}",
                "body": f"Test Body {i}"
            }
            for i in range(3)
        ]
        
        # Send the batch
        results = self.sender.send_batch(emails, max_retries=2)
        
        # Verify the results
        self.assertEqual(results['success'], 3)
        self.assertEqual(results['failure'], 0)
        self.assertEqual(self.mock_smtp_instance.send_message.call_count, 3)
        self.assertEqual(self.sender.sent_count, 3)
    
    def test_send_batch_with_retries(self):
        """Test batch sending with retries for failed emails."""
        # Set up the mock to fail on the first email
        original_side_effect = self.mock_smtp_instance.send_message.side_effect
        
        # Make the first call fail, then succeed
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt failed")
            return original_side_effect(*args, **kwargs)
            
        self.mock_smtp_instance.send_message.side_effect = side_effect
        
        # Prepare test data (just one email)
        emails = [{
            "to_email": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        }]
        
        # Send with retries
        results = self.sender.send_batch(emails, max_retries=3)
        
        # Verify the results
        self.assertEqual(results['success'], 1)
        self.assertEqual(results['failure'], 0)
        self.assertEqual(self.mock_smtp_instance.send_message.call_count, 2)
        self.mock_time.assert_called_once_with(EMAIL_VALIDATION['retry_delay'])
    
    def test_send_batch_permanent_failure(self):
        """Test batch sending with permanent failures."""
        # Set up the mock to always fail
        self.mock_smtp_instance.send_message.side_effect = Exception("Send failed")
        
        # Prepare test data
        emails = [
            {
                "to_email": f"recipient{i}@example.com",
                "subject": f"Test Subject {i}",
                "body": f"Test Body {i}"
            }
            for i in range(2)
        ]
        
        # Send the batch with limited retries
        results = self.sender.send_batch(emails, max_retries=2)
        
        # Verify the results
        self.assertEqual(results['success'], 0)
        self.assertEqual(results['failure'], 2)
        self.assertEqual(self.mock_smtp_instance.send_message.call_count, 4)  # 2 emails x 2 retries
        self.assertEqual(self.sender.sent_count, 0)
    
    def test_context_manager_usage(self):
        """Test using EmailSender as a context manager."""
        # Use the EmailSender as a context manager
        with self.sender as sender:
            # Verify it's the same instance
            self.assertIs(sender, self.sender)
            
            # Send an email within the context
            sender.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                body="Test Body"
            )
        
        # Verify close was called
        self.mock_smtp_instance.quit.assert_called_once()
    
    def test_email_sender_helper(self):
        """Test the email_sender helper function."""
        # Create a new mock for this test
        with patch('lead_generator.agents.email_sender.EmailSender') as mock_sender_class:
            mock_sender_instance = MagicMock()
            mock_sender_class.return_value = mock_sender_instance
            
            # Use the helper function
            with email_sender(self.test_config) as sender:
                # Verify the sender was created and returned
                mock_sender_class.assert_called_once_with(self.test_config)
                self.assertIs(sender, mock_sender_instance)
                
                # Send an email
                sender.send_email(
                    to_email="recipient@example.com",
                    subject="Test Subject",
                    body="Test Body"
                )
                mock_sender_instance.send_email.assert_called_once()
            
            # Verify close was called
            mock_sender_instance.smtp.quit.assert_called_once()
    
    def test_email_sender_helper_with_exception(self):
        """Test the email_sender helper with an exception."""
        # Create a new mock for this test
        with patch('lead_generator.agents.email_sender.EmailSender') as mock_sender_class:
            mock_sender_instance = MagicMock()
            mock_sender_class.return_value = mock_sender_instance
            
            # Simulate an exception in the context
            try:
                with email_sender(self.test_config) as sender:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Verify close was still called despite the exception
            mock_sender_instance.smtp.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main() 