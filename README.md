# Malaysian Lead Generator

A comprehensive system for generating high-quality sales leads for Malaysian universities and businesses by scraping business directories, government websites, and university staff directories.

## Features

- Automated scraping of multiple Malaysian business sources
- Intelligent filtering and lead qualification
- Contact information extraction and validation
- Automated personalized email outreach with proposal attachments
- Secure credential management and encryption
- Rate-limited API with robust security protections
- n8n workflow integration for visual automation
- Lead management and tracking system
- Detailed analytics and reporting

## Project Structure

```
/
├── lead_generator/            # Main package
│   ├── agents/                # Core functionality modules
│   │   ├── scraper.py         # Base scraper functionality
│   │   ├── yellow_pages_scraper.py
│   │   ├── gov_ministry_scraper.py
│   │   ├── university_scraper.py
│   │   ├── email_generator.py
│   │   ├── email_sender.py
│   ├── api/                   # API layer
│   │   ├── api_service.py     # API service connecting to core functions
│   │   ├── auth.py            # Authentication functions
│   │   ├── middleware.py      # Security middleware (rate limiting, logging)
│   │   ├── models.py          # Pydantic validation models
│   │   ├── routes.py          # API route definitions
│   ├── config/                # Configuration files
│   │   ├── email_config.py    # Email settings
│   │   ├── secure_config.py   # Secure credential management
│   │   ├── proposal_config.py # Proposal selection configuration
│   ├── database/              # Database models and queries
│   ├── prompts/               # Email templates
│   ├── utils/                 # Utility functions
│   ├── tests/                 # Test suites
├── n8n_workflows/             # n8n workflow exports
├── proposals/                 # PDF proposal storage
├── scripts/                   # Utility scripts
```

## Installation

### Prerequisites

- Python 3.8 or higher
- SMTP server access for email outreach
- n8n (optional, for workflow automation)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/malaysian-lead-generator.git
cd malaysian-lead-generator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the secure credential system:
```bash
python manage_credentials.py setup --create-env-template
```

4. Configure your environment:
```bash
cp .env.template .env
# Edit .env with your settings
```

5. Set proper permissions for security:
```bash
# On Linux/Mac
chmod 700 lead_generator/config/.secure
chmod 600 lead_generator/config/.secure/*
chmod 600 .env
```

## Usage

### Starting the Scrapers

To run the scraping system:

```bash
python run_scraper.bat
```

This will open an interactive menu that allows you to:
1. Configure scraping parameters
2. Select target sources
3. Set limits and filters
4. Import collected leads to the database

### API and Lead Management

Start the API server with:

```bash
python run_api.bat
```

The API includes:
- JWT-based authentication
- Role-based authorization
- Rate limiting
- Input validation
- Secure error handling

### Email Outreach

Send personalized emails to leads with:

```bash
python -m lead_generator.main --email-send --template default
```

For emails with PDF proposal attachments:
```bash
python -m lead_generator.main --email-send --attach-proposal path/to/proposal.pdf
```

## Security Features

The Malaysian Lead Generator implements comprehensive security measures:

### Credential Protection
- Fernet symmetric encryption for all sensitive credentials
- PBKDF2 key derivation with SHA-256
- Secure credential vault with master password protection
- Environment variable integration

### API Security
- JWT-based authentication with configurable expiration
- Specific CORS origins instead of wildcards
- Rate limiting based on client IP addresses
- Input validation and sanitization via Pydantic models
- Protection against injection attacks

### Email Security
- Rate limiting to prevent spam-flagging
- Attachment validation and size limits
- Email address verification

### Data Protection
- Input sanitization to prevent injection attacks
- Parameterized queries for database operations
- Proper error handling without information leakage

## Configuration

### Security Configuration

Configure security settings in `.env`:

```
# Master password for credential encryption
LEAD_GEN_MASTER_PASSWORD=your_secure_master_password

# API Security
API_SECRET_KEY=your_long_random_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
API_DEBUG=false

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://lead-generator.example.com
```

### Email Templates

Email templates are stored in `lead_generator/prompts/` as JSON files:

```json
{
  "subject": "Opportunity for {{organization}}",
  "body": "Dear {{person_name}},\n\nI noticed your work at {{organization}} and wanted to discuss..."
}
```

## n8n Workflow Integration

The system integrates with n8n for visual workflow automation:

1. Install n8n:
```bash
npm install n8n -g
```

2. Start n8n:
```bash
n8n start
```

3. Import workflows from the `n8n_workflows/` directory

## Troubleshooting

### Common Issues

- **API Rate Limiting**: Adjust the rate limit in `lead_generator/api/routes.py`
- **Encryption Key Issues**: Use `python manage_credentials.py reset-key` to regenerate keys
- **CORS Errors**: Update allowed origins in `.env` or directly in the API middleware
- **Email Delivery Issues**: Check SMTP settings and server reputation

## Maintenance

Run the cleanup utility to maintain system performance:
```bash
python cleanup_temp_files.py --all
```

## Contributing

Please review the `PLANNING.md` file for architecture details and coding standards before contributing.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 