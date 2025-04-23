#!/usr/bin/env python3
"""
Email validation and sanitization utilities.
"""

import re
import logging
from typing import Tuple, Optional
from email.utils import parseaddr

logger = logging.getLogger(__name__)

class EmailValidator:
    """Handles email validation and sanitization."""
    
    # Regular expression for basic email validation
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        'mailinator.com', 'tempmail.com', 'guerrillamail.com',
        'sharklasers.com', 'yopmail.com', 'throwawaymail.com'
    }
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """
        Validate an email address.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email address is empty"
        
        # Basic format check
        if not cls.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        # Parse email address
        _, email_addr = parseaddr(email)
        if not email_addr:
            return False, "Could not parse email address"
        
        # Check for disposable email domains
        domain = email_addr.split('@')[-1].lower()
        if domain in cls.DISPOSABLE_DOMAINS:
            return False, "Disposable email addresses are not allowed"
        
        return True, ""
    
    @classmethod
    def sanitize_email(cls, email: str) -> Optional[str]:
        """
        Sanitize an email address.
        
        Args:
            email: Email address to sanitize
            
        Returns:
            Sanitized email address or None if invalid
        """
        try:
            # Remove any whitespace
            email = email.strip()
            
            # Parse email address
            _, email_addr = parseaddr(email)
            if not email_addr:
                return None
            
            # Convert to lowercase
            email_addr = email_addr.lower()
            
            # Validate
            is_valid, _ = cls.validate_email(email_addr)
            if not is_valid:
                return None
            
            return email_addr
            
        except Exception as e:
            logger.error(f"Error sanitizing email {email}: {e}")
            return None
    
    @classmethod
    def is_disposable_domain(cls, domain: str) -> bool:
        """
        Check if a domain is a disposable email domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            True if domain is disposable
        """
        return domain.lower() in cls.DISPOSABLE_DOMAINS
    
    @classmethod
    def add_disposable_domain(cls, domain: str):
        """
        Add a domain to the disposable domains list.
        
        Args:
            domain: Domain to add
        """
        cls.DISPOSABLE_DOMAINS.add(domain.lower()) 