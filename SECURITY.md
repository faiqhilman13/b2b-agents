# Security Guide for Malaysian Lead Generator

This document outlines the security features implemented in the Malaysian Lead Generator project and provides guidelines for securely deploying and operating the system.

## Table of Contents

1. [Security Features](#security-features)
2. [Credential Management](#credential-management)
3. [Environment Setup](#environment-setup)
4. [Secure Deployment](#secure-deployment)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Security Features

### Credential Encryption
The system uses the industry-standard `cryptography` package to provide strong encryption for sensitive credentials:
- Fernet symmetric encryption for credential values
- PBKDF2 key derivation with SHA-256 for secure key generation
- Salt-based key generation to prevent rainbow table attacks

### Secure Configuration
A dedicated `SecureConfigManager` handles all sensitive configuration:
- Encrypted credential storage in a secure vault
- Environment variable integration with fallback mechanisms
- Separation of code and configuration concerns

### Credential Vault
All sensitive credentials are stored in an encrypted vault:
- Credentials are never stored in plain text on disk
- The vault itself is placed in a `.secure` directory that should be gitignored
- Only encrypted values are persisted

## Credential Management

### Prerequisites
Install required security dependencies:
```
pip install -r requirements.txt
```

### Initial Setup
To set up the credential storage system:
```
python manage_credentials.py setup --create-env-template
```

This will:
1. Create a master encryption key protected by your password
2. Generate a `.env.template` file with required configuration variables
3. Initialize the secure storage vault

### Managing Credentials
The utility provides several commands for credential management:

#### Adding Credentials
```
python manage_credentials.py add --key SMTP_PASSWORD --value "your-secure-password"
```
Or simply:
```
python manage_credentials.py add
```
And follow the interactive prompts.

#### Listing Credentials
```
python manage_credentials.py list
```

#### Retrieving a Credential
```
python manage_credentials.py get --key SMTP_PASSWORD
```

#### Generating a .env File
```
python manage_credentials.py gen-env --output .env
```

## Environment Setup

### .env File
The project supports a `.env` file for environment configuration:

1. Copy the generated `.env.template` to `.env`
2. Fill in all the required values
3. Keep this file secure and never commit it to version control

Example `.env` file:
```
# Master password for credential encryption
LEAD_GEN_MASTER_PASSWORD=your_secure_master_password

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=Your Name

# Email Rate Limiting
EMAIL_RATE_LIMIT=100
EMAIL_BATCH_SIZE=10
EMAIL_DELAY=2.0
```

### Configuration Hierarchy
The system uses the following hierarchy to resolve configuration values:
1. Command-line arguments (highest priority)
2. Environment variables
3. Credential vault
4. Default values (lowest priority)

## Secure Deployment

### Pre-deployment Checklist
Before deploying to production, ensure:

1. All sensitive credentials are stored in the encrypted vault
2. The `.env` file is properly configured
3. The `cryptography` package is installed
4. The `.secure` directory has appropriate permissions

### Directory Security
Set proper permissions on sensitive directories:
```
chmod 700 lead_generator/config/.secure
chmod 600 lead_generator/config/.secure/*
chmod 600 .env
```

### Gitignore Configuration
Ensure the following entries are in your `.gitignore` file:
```
# Security-related files
.env
.env.*
!.env.template
lead_generator/config/.secure/
*.pem
*.key
```

## Best Practices

### Password Policies
- Use strong master passwords (minimum 12 characters)
- Include a mix of uppercase, lowercase, numbers, and special characters
- Avoid dictionary words and common patterns
- Do not reuse passwords across different systems

### Credential Rotation
- Regularly rotate all credentials, especially for production systems
- Update the credential vault after each rotation
- Consider implementing an automated credential rotation policy

### Access Control
- Limit access to the credential management utility
- Only grant necessary permissions to users
- Use separate credentials for development and production

### Logging and Monitoring
- Monitor access to sensitive configuration files
- Log credential usage but never log credential values
- Review logs regularly for unauthorized access attempts

## Troubleshooting

### Common Issues

#### Encryption Key Issues
If you encounter errors related to encryption keys:
```
Error: Could not decrypt credentials.
```

Solutions:
1. Verify that the master password is correct
2. Check if the key file exists in `.secure/.keyfile`
3. Ensure the `cryptography` package is installed

#### Environment Variable Problems
If environment variables aren't being recognized:
```
Warning: SMTP configuration not found in environment.
```

Solutions:
1. Verify the `.env` file exists and contains the required variables
2. Check that the file permissions allow the application to read it
3. Try loading the variables manually:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

#### Access Permission Errors
If you see permission errors when accessing the vault:
```
PermissionError: [Errno 13] Permission denied: './.secure/credential_vault.json'
```

Solutions:
1. Check the file permissions on the `.secure` directory
2. Ensure the application has write permissions if setting credentials
3. Set appropriate ownership of the security files 