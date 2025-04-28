# MCP-Powered Data Sources Workflow

## Overview

The Malaysian Lead Generator now leverages MCP-powered Apify Actors for reliable data acquisition. This document explains how to use the new workflow to collect, enrich, and process leads from multiple sources.

## Available Data Sources

### 1. Google Maps Client

The Google Maps Client provides access to business information from Google Maps, including:

- Business names, addresses, and contact information
- Geographic coordinates
- Ratings and reviews
- Business categories
- Opening hours and other metadata

### 2. Instagram Client

The Instagram Client extracts business information from Instagram profiles and posts:

- Profile details (biography, contact info)
- Post content with contact information
- Business categories
- Social media metrics
- Location information

### 3. Web Browser Client

The Web Browser Client can search the web and extract content from websites:

- Extract contact information from business websites
- Search for specific business information
- Access content that would normally be blocked by anti-scraping measures
- Parse structured content from web pages

## Using the Command Line Interface

The updated CLI provides easy access to the MCP-powered data sources. Here are some example commands:

### Google Maps Search

```bash
# Search for software companies in Kuala Lumpur
scripts\run_lead_generator.bat --use-google-maps --search "software development" --location "Kuala Lumpur" --limit 20

# Search for engineering firms in Penang
scripts\run_lead_generator.bat --use-google-maps --search "engineering consulting" --location "Penang" --limit 15
```

### Instagram Search

```bash
# Search for business accounts with specific hashtag
scripts\run_lead_generator.bat --use-instagram --search "#malaysiabusiness" --limit 10

# Search for a specific business username
scripts\run_lead_generator.bat --use-instagram --search "@techcompanymalaysia" --limit 5
```

### Web Browser Search

```bash
# Search and extract content about Malaysian businesses
scripts\run_lead_generator.bat --use-web-browser --search "top software companies in Malaysia" --limit 3

# Extract content from a specific website
scripts\run_lead_generator.bat --use-web-browser --url "https://example-business.com" 
```

### Multi-Source Enrichment

```bash
# Use multiple data sources and enrich leads
scripts\run_lead_generator.bat --multi-source --search "technology companies Malaysia" --location "Kuala Lumpur" --limit 10

# Specify which sources to use
scripts\run_lead_generator.bat --use-google-maps --use-web-browser --search "digital agencies Malaysia" --location "Petaling Jaya" --limit 5
```

## Email Generation with Enhanced Data

The email templates have been updated to take advantage of the rich data available from MCP-powered sources:

```bash
# Generate emails with enhanced data
scripts\run_lead_generator.bat --generate-emails --email-template default

# Generate and send emails with category-based proposal selection
scripts\run_lead_generator.bat --generate-emails --send-emails --use-package-selection --smtp-server your.smtp.server --smtp-username user --smtp-password pass --from-email your@email.com
```

## Working with n8n Workflows

We've created an updated n8n workflow that leverages the multi-source capabilities:

1. Install and set up n8n if you haven't already
2. Start the API server: `scripts\run_api.bat`
3. Import the workflow from `n8n_workflows/lead_acquisition.json`
4. Configure the workflow with your API credentials
5. Run the workflow to collect and process leads

## Targeting Strategy

The system now includes an intelligent targeting strategy based on business categories:

- **High Priority Targets**: Technology companies, consulting firms, digital agencies
- **Medium Priority Targets**: Business services, education, event management
- **Low Priority Targets**: Retail, hospitality, general businesses

The targeting strategy automatically:

1. Determines the appropriate tier for each lead
2. Selects the most suitable email template
3. Matches the right proposal package
4. Sets appropriate follow-up timing

## Configuration

The MCP-powered workflow is configured through environment variables. Create a `.env` file based on the template:

```
# API Endpoints
GMAPS_API_ENDPOINT=https://your-mcp-endpoint/gmaps-proxy
INSTAGRAM_API_ENDPOINT=https://your-mcp-endpoint/instagram-scraper
WEB_BROWSER_API_ENDPOINT=https://your-mcp-endpoint/rag-web-browser

# Authentication
APIFY_API_KEY=your_apify_api_key

# Client Configuration
AUTO_ACTIVATE_CLIENTS=true
DEFAULT_CACHE_TTL=86400
MAX_RETRIES=3
REQUEST_TIMEOUT=60
```

## Common Issues and Solutions

### API Connection Problems

If you encounter connection issues:

1. Verify your API key and endpoints in the `.env` file
2. Check network connectivity to the MCP server
3. Increase timeout settings if needed: `REQUEST_TIMEOUT=120`

### No Results Found

If searches return no results:

1. Try more general search terms
2. Check location spelling for Google Maps searches
3. Try different hashtags for Instagram searches
4. Use the `--limit` parameter to request more results

### Error in Multi-Source Enrichment

If enrichment fails:

1. Try running each data source individually first
2. Check that all API endpoints are properly configured
3. Verify that output directory is writable

## Best Practices

1. **Start with Google Maps**: The most reliable data source for business contacts
2. **Enrich with Instagram**: Add social media insights to leads from Google Maps
3. **Validate with Web Browser**: Extract additional contact information from business websites
4. **Use Multi-Source Mode**: Let the system handle deduplication and enrichment automatically
5. **Use Package Selection**: Let the targeting strategy select the most appropriate proposal

## Next Steps

1. For custom targeting strategies, modify `lead_generator/config/targeting_config.py`
2. For custom proposal selection, modify `lead_generator/config/proposal_config.py`
3. For custom email templates, add new templates to `lead_generator/prompts/` 