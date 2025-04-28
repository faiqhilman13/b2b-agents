#!/usr/bin/env python3
"""
Email configuration settings.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# Import secure configuration if available
try:
    from .secure_config import secure_config
    SECURE_CONFIG_AVAILABLE = True
except ImportError:
    SECURE_CONFIG_AVAILABLE = False
    logger.warning("Secure configuration module not found. Falling back to environment variables.")

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

# SMTP Configuration - Use secure config if available
if SECURE_CONFIG_AVAILABLE:
    SMTP_CONFIG = secure_config.get_smtp_config()
else:
    SMTP_CONFIG: Dict[str, Any] = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', ''),
        'from_name': os.getenv('FROM_NAME', 'Lead Generator'),
        'rate_limit': int(os.getenv('EMAIL_RATE_LIMIT', 100)),  # emails per hour
        'batch_size': int(os.getenv('EMAIL_BATCH_SIZE', 10)),
        'delay_between_sends': float(os.getenv('EMAIL_DELAY', 2.0))  # seconds
    }

# Load JSON templates
def load_template(filename):
    try:
        template_path = PROMPTS_DIR / filename
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading template {filename}: {e}")
        return None

# Template loading
DEFAULT_TEMPLATE = load_template("default.json")
GOVERNMENT_TEMPLATE = load_template("government.json") 
UNIVERSITY_TEMPLATE = load_template("university.json")

# Email Templates
EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {
    'default': {
        'subject': DEFAULT_TEMPLATE['subject'] if DEFAULT_TEMPLATE else "Exploring Potential Collaboration with {organization}",
        'body': DEFAULT_TEMPLATE['body'] if DEFAULT_TEMPLATE else "Default template body"
    },
    'government': {
        'subject': GOVERNMENT_TEMPLATE['subject'] if GOVERNMENT_TEMPLATE else "Proposal for Partnership with {organization}",
        'body': GOVERNMENT_TEMPLATE['body'] if GOVERNMENT_TEMPLATE else "Government template body"
    },
    'university': {
        'subject': UNIVERSITY_TEMPLATE['subject'] if UNIVERSITY_TEMPLATE else "Research Collaboration Opportunity with {organization}",
        'body': UNIVERSITY_TEMPLATE['body'] if UNIVERSITY_TEMPLATE else "University template body"
    },
    'lead_followup': {
        'subject': "Following up about {organization}",
        'body': """
        Dear {person_name},

        I hope this email finds you well. I came across {organization} while researching {industry} companies in Malaysia.

        I would love to learn more about your services and explore potential collaboration opportunities. Would you be available for a brief call or meeting to discuss this further?

        Best regards,
        {sender_name}
        """
    }
}

# Email Validation - Get values from secure config if available
if SECURE_CONFIG_AVAILABLE:
    EMAIL_VALIDATION = {
        'max_retries': int(secure_config.get_credential('EMAIL_MAX_RETRIES', 3)),
        'retry_delay': int(secure_config.get_credential('EMAIL_RETRY_DELAY', 60)),
        'timeout': int(secure_config.get_credential('EMAIL_TIMEOUT', 30)),
        'blacklist_domains': secure_config.get_credential('EMAIL_BLACKLIST_DOMAINS', 
                                                         'example.com,test.com,invalid.com,domain.com').split(','),
        'verify_recipients': secure_config.get_credential('EMAIL_VERIFY_RECIPIENTS', 'true').lower() == 'true',
        'max_attachment_size': int(secure_config.get_credential('EMAIL_MAX_ATTACHMENT_SIZE', 10 * 1024 * 1024))
    }
else:
    EMAIL_VALIDATION = {
        'max_retries': 3,
        'retry_delay': 60,  # seconds
        'timeout': 30,  # seconds
        'blacklist_domains': [
            'example.com',
            'test.com',
            'invalid.com',
            'domain.com'
        ],
        'verify_recipients': True,
        'max_attachment_size': 10 * 1024 * 1024  # 10MB
    }

# Logging Configuration - Get values from secure config if available
if SECURE_CONFIG_AVAILABLE:
    EMAIL_LOGGING = {
        'log_file': os.path.join(secure_config.get_credential('LOG_DIR', '.'), 'email_logs.log'),
        'max_file_size': int(secure_config.get_credential('EMAIL_LOG_MAX_SIZE', 10 * 1024 * 1024)),
        'backup_count': int(secure_config.get_credential('EMAIL_LOG_BACKUP_COUNT', 5)),
        'level': secure_config.get_credential('EMAIL_LOG_LEVEL', 'INFO'),
        'include_timestamp': secure_config.get_credential('EMAIL_LOG_TIMESTAMP', 'true').lower() == 'true'
    }
else:
    EMAIL_LOGGING = {
        'log_file': os.path.join(os.getenv('LOG_DIR', '.'), 'email_logs.log'),
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'level': os.getenv('EMAIL_LOG_LEVEL', 'INFO'),
        'include_timestamp': True
    }

# Sending policies - Get values from secure config if available
if SECURE_CONFIG_AVAILABLE:
    EMAIL_POLICIES = {
        'send_limit_per_day': int(secure_config.get_credential('DAILY_EMAIL_LIMIT', 200)),
        'cooldown_period': int(secure_config.get_credential('COOLDOWN_PERIOD', 24)),
        'max_recipients_per_mail': int(secure_config.get_credential('MAX_RECIPIENTS', 1)),
        'retry_failed': secure_config.get_credential('RETRY_FAILED_EMAILS', 'true').lower() == 'true',
        'track_opens': secure_config.get_credential('TRACK_OPENS', 'false').lower() == 'true'
    }
else:
    EMAIL_POLICIES = {
        'send_limit_per_day': int(os.getenv('DAILY_EMAIL_LIMIT', 200)),
        'cooldown_period': int(os.getenv('COOLDOWN_PERIOD', 24)),  # hours between repeat emails
        'max_recipients_per_mail': int(os.getenv('MAX_RECIPIENTS', 1)),
        'retry_failed': True,
        'track_opens': os.getenv('TRACK_OPENS', 'false').lower() == 'true'
    } 