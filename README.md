# Malaysian Lead Generator

A tool for collecting business contacts from Malaysian sources and generating personalized email outreach with proposal attachments.

## Project Structure

The project follows a clean, modular structure:

```
/
├── lead_generator/            # Main package
│   ├── agents/                # Core functionality modules
│   │   ├── api_clients/       # API-based data acquisition
│   │   │   ├── base_client.py # Base API client
│   │   │   ├── gmaps_client.py # Google Maps integration
│   │   │   ├── instagram_client.py   # Instagram integration  
│   │   │   ├── web_browser_client.py # RAG Web Browser integration
│   │   ├── scrapers/          # Legacy scrapers (deprecated)
│   │   │   ├── scraper.py     # Base scraper functionality
│   │   │   ├── yellow_pages_scraper.py
│   │   │   ├── gov_ministry_scraper.py
│   │   │   ├── university_scraper.py
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
│   │   ├── api_config.py      # API credentials and configuration
│   ├── database/              # Database models and queries
│   │   ├── models.py          # SQLite schema definitions
│   │   ├── queries.py         # Database operation functions
│   ├── prompts/               # Email templates
│   │   ├── default.json       # Various email templates
│   ├── utils/                 # Utility functions
│   │   ├── cache.py           # Deduplication and tracking
│   │   ├── email_validator.py # Email validation
│   │   ├── data_processor.py  # Data standardization
│   ├── tests/                 # Test suites
│       ├── unit/              # Unit tests
│           ├── test_api_clients.py # Tests for API integrations
│           ├── test_scrapers.py    # Legacy scraper tests
│           ├── test_email_sender.py
├── scripts/                   # Utility scripts
│   ├── run_lead_generator.bat # Script to run the lead generator
│   ├── run_api.bat            # Script to run the API server
│   ├── cleanup_temp_files.py  # Utility for cleaning temporary files
│   ├── fix_imports.py         # Utility for fixing imports
├── n8n_workflows/             # n8n workflow exports
├── proposals/                 # PDF proposal storage
├── output/                    # Output directory for data
├── logs/                      # Log files
├── requirements.txt           # Project dependencies
├── PLANNING.md                # Project architecture and standards
├── SECURITY.md                # Security guidelines
├── TASK.md                    # Task tracking
```

## Features

- **Lead Collection**: Collect business contact information using reliable data sources:
  - Google Maps data for business locations, contacts, and ratings
  - Instagram profiles for social media presence and engagement
  - Website content extraction for additional business information

- **Data Standardization**: Unified pipeline for processing data from multiple sources:
  - Standardize data from different sources into a common format
  - Enrich leads by combining data from multiple sources
  - Deduplicate leads based on organization, email, phone, and website
  - Calculate lead completeness scores for quality assessment

- **Email Generation**: Create personalized emails using templates with dynamic variables

- **Email Sending**: Send emails with PDF proposal attachments

- **API**: RESTful API for accessing and managing leads

## Data Sources

The project uses MCP-powered Apify Actors for reliable data acquisition:

### Google Maps Proxy (Implemented)
- Access to thousands of Malaysian businesses with accurate location information
- Extract business names, addresses, phone numbers, websites, and ratings
- Target specific business categories and geographic areas
- Filter and sort by ratings, popularity, and other criteria

### Instagram Scraper (In Progress)
- Extract information from business Instagram profiles
- Access post content, follower counts, and engagement metrics
- Identify business contact information shared in profiles
- Gather insights into business activities and marketing focus

### RAG Web Browser (Implemented)
- Search and extract content from business websites
- Perform targeted research to find specific business information
- Bypass anti-scraping measures through Apify infrastructure
- Extract structured content for data enrichment

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
# Run the lead generator with Google Maps data source
scripts\run_lead_generator.bat --use-google-maps --search "engineering firms malaysia" --limit 50

# Run the lead generator with RAG Web Browser data source
scripts\run_lead_generator.bat --use-web-browser --search "engineering consultants kuala lumpur" --limit 20

# Run the lead generator with Instagram data source (coming soon)
scripts\run_lead_generator.bat --use-instagram --search "@malaysiabusiness" --limit 30

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

## API Client Usage

The project uses MCP-powered Apify Actors for data acquisition through client adapters:

### Setup

1. **Environment Configuration**: 
   Configure API endpoint environment variables in your `.env` file:
   ```
   GMAPS_API_ENDPOINT=https://your-mcp-endpoint/gmaps-proxy
   WEB_BROWSER_API_ENDPOINT=https://your-mcp-endpoint/rag-web-browser
   INSTAGRAM_API_ENDPOINT=https://your-mcp-endpoint/instagram-scraper
   AUTO_ACTIVATE_CLIENTS=true
   ```

2. **Client Activation**:
   Clients can be activated programmatically or automatically:
   ```python
   from lead_generator.agents.api_clients import activate_clients, get_client
   
   # Automatic activation (uses environment variables)
   google_maps_client = get_client('google_maps')
   
   # Manual activation with custom endpoints
   clients = activate_clients({
       'google_maps': 'https://custom-endpoint/gmaps-proxy',
       'web_browser': 'https://custom-endpoint/rag-web-browser'
   })
   ```

### Google Maps Client Usage

```python
from lead_generator.agents.api_clients import get_client

# Get the client instance
gmaps_client = get_client('google_maps')

# Search for businesses
businesses = gmaps_client.search_businesses(
    query="accounting firms",
    location="Kuala Lumpur",
    limit=10
)

# Get detailed information about a specific business
business_details = gmaps_client.get_business_details(place_id="place_123abc")

# Search by location and category
nearby_businesses = gmaps_client.search_by_location(
    category="restaurants",
    location="Petaling Jaya",
    radius_km=5.0
)
```

### Web Browser Client Usage

```python
from lead_generator.agents.api_clients import get_client

# Get the client instance
web_client = get_client('web_browser')

# Search and extract content
search_results = web_client.search_and_extract(
    query="software development company malaysia",
    max_results=3
)

# Extract content from a specific URL
website_content = web_client.extract_from_url(
    url="https://example.com",
    output_format="markdown"
)

# Search for a specific business and extract contact information
business_info = web_client.search_for_business(
    business_name="ABC Tech",
    location="Kuala Lumpur"
)
```

### Unified Data Standardization

The project includes a powerful unified data standardization pipeline that processes and enriches lead data from multiple sources:

```python
from lead_generator.utils.data_processor import standardize_lead, enrich_lead, deduplicate_leads

# Standardize data from different sources
google_data = gmaps_client.search_businesses(query="accounting firms Kuala Lumpur", limit=10)
for business in google_data:
    lead = standardize_lead(business, "google_maps")
    # Process standardized lead...

# Enrich leads with data from multiple sources
lead_from_maps = standardize_lead(maps_data, "google_maps")
lead_from_instagram = standardize_lead(instagram_data, "instagram")
lead_from_web = standardize_lead(web_data, "web_browser")

# Combine all data into a rich lead profile
enriched_lead = enrich_lead(lead_from_maps, [lead_from_instagram, lead_from_web])

# Work with a collection of leads
all_leads = [lead1, lead2, lead3, lead4]  # Some leads may be duplicates
unique_leads = deduplicate_leads(all_leads)  # Removes duplicates and merges data

# Get statistics about your leads
from lead_generator.utils.data_processor import get_lead_statistics
stats = get_lead_statistics(all_leads)
print(f"Total leads: {stats['total_leads']}")
print(f"Completeness: {stats['completeness']['average_score']}%")
```

The standardization pipeline handles:
- Malaysian address parsing and normalization
- Phone number standardization
- Contact information extraction from text
- Lead deduplication and enrichment
- Quality scoring and filtering

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