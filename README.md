# Malaysian Lead Generator

A tool for collecting business contacts from Malaysian sources and generating personalized email outreach with proposal attachments.

## Project Structure

The project follows a clean, modular structure:

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
│   │   ├── routes.py          # API route definitions
│   │   ├── app.py             # FastAPI application
│   ├── config/                # Configuration files
│   │   ├── email_config.py    # Email settings
│   │   ├── secure_config.py   # Secure credential management
│   │   ├── proposal_config.py # Proposal selection configuration
│   ├── database/              # Database models and queries
│   │   ├── models.py          # SQLite schema definitions
│   │   ├── queries.py         # Database operation functions
│   ├── prompts/               # Email templates
│   │   ├── default.json       # Various email templates
│   ├── utils/                 # Utility functions
│   │   ├── cache.py           # Deduplication and tracking
│   │   ├── email_validator.py # Email validation
│   ├── tests/                 # Test suites
│       ├── unit/              # Unit tests
│           ├── test_scrapers.py
│           ├── test_email_sender.py
├── scripts/                   # Utility scripts
│   ├── run_lead_generator.bat # Script to run the lead generator
│   ├── run_api.bat            # Script to run the API server
│   ├── cleanup_temp_files.py  # Utility for cleaning temporary files
│   ├── fix_imports.py         # Utility for fixing imports
├── n8n_workflows/             # n8n workflow exports
├── proposals/                 # PDF proposal storage
├── output/                    # Output directory for scraped data
├── logs/                      # Log files
├── requirements.txt           # Project dependencies
├── PLANNING.md                # Project architecture and standards
├── SECURITY.md                # Security guidelines
├── TASK.md                    # Task tracking
```

## Features

- **Lead Collection**: Scrape contact information from:
  - Yellow Pages Malaysia
  - Government ministry websites
  - University staff directories

- **Email Generation**: Create personalized emails using templates with dynamic variables

- **Email Sending**: Send emails with PDF proposal attachments

- **API**: RESTful API for accessing and managing leads

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/malaysian-lead-generator.git
   cd malaysian-lead-generator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.template`:
   ```
   cp .env.template .env
   ```

4. Edit `.env` with your credentials (API keys, email settings, etc.)

## Usage

### Command-line Interface

Use the provided batch scripts for easy execution:

```
# Run the lead generator (scraper)
scripts\run_lead_generator.bat --all --pages 5

# Generate emails without sending
scripts\run_lead_generator.bat --generate

# Generate and send emails with a proposal 
scripts\run_lead_generator.bat --send --package meeting --live

# Get help
scripts\run_lead_generator.bat --help
```

### API Server

Start the API server:

```
# Development mode
scripts\run_api.bat 

# Production mode
scripts\run_api.bat --production
```

The API will be available at http://localhost:8000

## API Endpoints

- **GET /leads**: Get all leads
- **GET /leads/{id}**: Get lead by ID
- **POST /leads**: Create a new lead
- **PUT /leads/{id}**: Update a lead
- **DELETE /leads/{id}**: Delete a lead
- **POST /token**: Get authentication token

For detailed API documentation, visit http://localhost:8000/docs when the server is running.

## Development

Please follow the coding standards and architecture defined in `PLANNING.md`.

### Testing

Run the unit tests:

```
pytest lead_generator/tests/
```

## Security

This project implements strong security practices for handling credentials and email operations. See `SECURITY.md` for details.

## License

[Insert License Information] 