# Malaysian Lead Generator Project Notes

## Project Overview
The Malaysian Lead Generator is a tool designed to collect business contacts primarily via reliable data sources (APIs, open data) and supplement with targeted web scraping, then generate personalized outreach emails. The project is divided into distinct phases:

1. **Lead Collection** - Acquiring business contacts (API-first, supplemented by scraping)
2. **Email Generation** - Creating personalized outreach emails
3. **Email Sending** - Automating the email sending process
4. **Tracking & Analytics** - Monitoring response rates and campaign effectiveness
5. **Maintenance & Utilities** - Tools for system maintenance and cleanup
6. **Security & Compliance** - Ensuring data protection and secure operations
7. **n8n Workflow Automation** - Integration with n8n for workflow automation and UI
8. **Agentive Frontend Integration** - Web-based user interface for the system

## Current Status
We have completed a major project reorganization to follow Python best practices, creating a clean, modular package structure within the lead_generator package.

We have completed implementations for Email Generation (Phase 2), Email Sending (Phase 3 - including intelligent PDF proposal attachments), Maintenance Utilities (Phase 5 - including configurable cleanup), Security (Phase 6 - including recent enhancements like specific CORS, rate limiting, Pydantic validation, secure error handling, improved token handling), and n8n Workflow Automation (Phase 7 - including API layer and workflows). All functional components are integrated via a comprehensive CLI and the n8n API.

**MAJOR BREAKTHROUGH (June 10, 2024)**: We have successfully integrated MCP-powered Apify Actors to solve our lead acquisition challenges. This integration provides three powerful, reliable data sources:

1. **Google Maps Proxy (gmaps-proxy)** - Access to thousands of Malaysian businesses with accurate location, contact, and rating information
2. **Instagram Scraper** - Capability to extract business information from social media profiles and posts
3. **RAG Web Browser** - Ability to search and extract structured content from websites without anti-scraping limitations

This breakthrough resolves our primary blocker and unlocks the path to completing the entire system.

Initial progress on the Agentive Frontend Integration (Phase 8) API foundation is complete, and UI development can now proceed as the data acquisition issue has been resolved.

## Project Structure
```
/
├── lead_generator/            # Main package
│   ├── agents/                # Core functionality modules
│   │   ├── api_clients/       # API-based data acquisition (NEW)
│   │   │   ├── base_client.py # Base API client functionality
│   │   │   ├── google_maps_client.py # Google Maps Proxy integration
│   │   │   ├── instagram_client.py   # Instagram Scraper integration
│   │   │   ├── web_browser_client.py # RAG Web Browser integration
│   │   ├── scraper.py         # Base scraper functionality (legacy)
│   │   ├── yellow_pages_scraper.py   # Legacy scraper (deprecated)
│   │   ├── gov_ministry_scraper.py   # Legacy scraper (deprecated)
│   │   ├── university_scraper.py     # Legacy scraper (deprecated)
│   │   ├── email_generator.py
│   │   ├── email_sender.py    # Email sending module (Updated with attachment support)
│   ├── api/                   # API layer for n8n integration
│   │   ├── api_service.py     # API service connecting core functionality
│   │   ├── auth.py            # Authentication and authorization
│   │   ├── models.py          # Pydantic models for validation
│   │   ├── middleware.py      # Rate limiting and security middleware
│   │   ├── routes.py          # API route definitions
│   │   ├── app.py             # FastAPI application
│   ├── config/                # Configuration files
│   │   ├── email_config.py    # Email settings configuration
│   │   ├── secure_config.py   # Secure credential management
│   │   ├── proposal_config.py # Proposal selection configuration
│   │   ├── api_config.py      # API credentials and configuration (NEW)
│   │   ├── .secure/           # Encrypted credential storage (not in VCS)
│   ├── database/              # Database models and queries
│   │   ├── models.py          # SQLite schema definitions (to be enhanced)
│   │   ├── queries.py         # Database operation functions
│   ├── prompts/               # Email templates
│   │   ├── default.json
│   │   ├── government.json
│   │   ├── university.json
│   │   ├── retreat.json
│   │   ├── cost.json
│   │   ├── exec_tone.json
│   ├── utils/                 # Utility functions
│   │   ├── cache.py           # Deduplication and generation tracking
│   │   ├── email_validator.py # Email validation utilities
│   │   ├── data_processor.py  # Data standardization module (NEW)
│   ├── tests/                 # Test suites
│   │   ├── unit/
│   │       ├── test_api_clients.py # Tests for MCP-powered clients (NEW)
│   │       ├── test_scrapers.py    # Legacy scraper tests
│   │       ├── test_email_sender.py
│   │       ├── test_email_generator.py
│   ├── main.py                # Main entry point for CLI (to be updated)
├── scripts/                   # Utility scripts
│   ├── run_lead_generator.bat # Script to run the lead generator
│   ├── run_api.bat            # Script to run the API server
│   ├── run_scraper.bat        # Legacy batch script (deprecated)
│   ├── cleanup_temp_files.py  # Utility for cleaning temporary files
│   ├── cleanup_temp_files.bat # Batch file for cleanup operations
│   ├── fix_imports.py         # Utility to fix import statements
├── proposals/                 # Directory for PDF proposal files
├── n8n_workflows/             # Directory containing n8n workflow exports
│   ├── lead_acquisition.json  # NEW workflow using MCP-powered data sources
│   ├── email_generation.json  # Email generation workflow
│   ├── email_sending.json     # Email sending workflow
│   ├── email_sending_with_proposals.json  # Email sending with PDF attachments workflow
│   ├── analytics.json         # Analytics and reporting workflow
├── output/                    # Output directory for data
├── logs/                      # Log files directory
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── PLANNING.md                # Project architecture and standards
├── TASK.md                    # Task tracking and management
├── SECURITY.md                # Security guide and best practices
├── PROPOSAL_GUIDE.md          # Guide for using the package-based proposal system
├── IMPLEMENTATION_SUMMARY.md  # Technical implementation summary
├── PROJECT_NOTES.md           # Project status and planning
```

## Completed Tasks

### Project Reorganization Phase (COMPLETED)
1. ✅ Reorganized the project into a proper Python package structure (lead_generator)
2. ✅ Created a clean, modular directory structure following Python best practices
3. ✅ Moved all core functionality into the lead_generator package
4. ✅ Separated utility scripts into a dedicated scripts directory
5. ✅ Updated import paths and file references to work with new structure
6. ✅ Created appropriate __init__.py files
7. ✅ Removed duplicate files and cleaned up the project structure

### Data Acquisition Phase (BREAKTHROUGH ACHIEVED)
1. ✅ Identified reliable data sources through MCP-powered Apify Actors
   - ✅ Google Maps Proxy for business locations and contact information
   - ✅ Instagram Scraper for social media presence and engagement
   - ✅ RAG Web Browser for website content extraction and search
2. ✅ Determined API client infrastructure requirements
   - ✅ Identified adapter pattern for standardizing responses
   - ✅ Planned caching strategies to optimize API usage
   - ✅ Documented authentication and error handling needs
3. ❌ (DEPRIORITIZED) Legacy scrapers facing reliability issues

### Email Generation Phase (COMPLETED)
1. ✅ Created email_generator.py with template loading and personalization
2. ✅ Implemented multiple email templates (prompts/)
3. ✅ Built cache system (utils/cache.py)
4. ✅ Created SQLite schema (database/models.py)
5. ✅ Implemented database queries (database/queries.py)

### Email Sending Phase (COMPLETED)
1. ✅ Created email_config.py
2. ✅ Implemented email_sender.py (SMTP, rate limiting, batching, retries, attachments)
3. ✅ Added email_validator.py
4. ✅ Created tests for email sender
5. ✅ Implemented intelligent package-based proposal selection

### Integration Phase (COMPLETED)
1. ✅ Updated main.py to integrate core components
2. ✅ Updated batch scripts (run_lead_generator.bat) for integrated workflow
3. ✅ Established workflow from (test) lead data to email sending

### Maintenance & Utilities Phase (COMPLETED)
1. ✅ Created cleanup_temp_files.py and cleanup_temp_files.bat
2. ✅ Implemented configurable retention and intelligent cache cleaning
3. ✅ Added test_data.py, fix_imports.py
4. ✅ Enhanced error handling and backup creation

### Security & Compliance Phase (COMPLETED)
1. ✅ Implemented secure credential management (secure_config.py, encryption, vault)
2. ✅ Enhanced configuration security (dotenv, fallback)
3. ✅ Added manage_credentials.py, SECURITY.md, .env.template
4. ✅ Implemented credential rotation/access control considerations
5. ✅ Recent Enhancements: Restricted CORS, added API rate limiting, Pydantic validation, secure error handling, improved token handling

### n8n Workflow Automation Phase (COMPLETED)
1. ✅ Developed API Service Layer (api/api_service.py, api/routes.py, api/app.py)
2. ✅ Enhanced Database Models (database/models.py - DashboardStats, LeadStatus)
3. ✅ Created API Routes with FastAPI (including auth, validation)
4. ✅ Developed n8n Workflows (n8n_workflows/) for core processes
5. ✅ Implemented Security Measures (JWT, secure n8n creds, RBAC concept)
6. ✅ Created basic API testing infrastructure (api/tests/test_api.py)

## Current Issues and Limitations
- **Data Acquisition Issue RESOLVED**: MCP-powered Apify Actors now provide reliable data sources
- **Implementation In Progress**: Need to create client adapters and standardization pipeline
- n8n integration requires separate setup.
- **Incomplete Test Suite**: Missing comprehensive unit, integration, and end-to-end tests.
- **Web Frontend Not Implemented**: System currently relies on CLI/batch files and n8n UI.

## Next Steps (Revised Priorities)

### PRIORITY 1: MCP-Powered Apify Integration (HIGHEST PRIORITY)
1. **Implement Client Adapters**: Create adapter classes for each MCP-powered Apify Actor:
   - Develop GoogleMapsClient for business location and contact data
   - Implement InstagramClient for social media profile extraction
   - Create WebBrowserClient for targeted website content extraction
   - Build a unified data standardization pipeline

2. **Enhance Database Model**: Update database schema to accommodate rich API data:
   - Add social media profile fields for Instagram data
   - Include location and rating fields for Google Maps data
   - Add data source tracking and timestamp fields
   - Create migration path for existing data

3. **Update Workflow Integration**: 
   - Refactor main.py to prioritize MCP-powered data sources
   - Update n8n workflows to leverage multi-source data enrichment
   - Adjust email templates to utilize new data points
   - Implement intelligent lead scoring based on data completeness

4. **Implement Multi-Source Enrichment**:
   - Create enrichment pipeline to combine data from multiple sources
   - Develop validation and deduplication for multi-source data
   - Enhance proposal matching using richer lead data
   - Implement intelligent targeting based on business categories

### PRIORITY 2: Agentive Frontend Integration (UNBLOCKED - READY TO IMPLEMENT)
1. **Implement Frontend**: Build the user-friendly web interface using Lovable or another suitable modern framework based on the established "Agentive Frontend Integration Roadmap".
2. **Connect Frontend to API**: Integrate the UI with the existing FastAPI backend (lead_generator/api/).
3. **Develop Core UI Features**: Implement dashboard, lead management, email campaign management, proposal selection UI, and analytics visualization.
4. **Usability Testing**: Conduct testing to ensure the UI is intuitive and meets user needs.

### PRIORITY 3: Enhance Core Features & Testing
1. **Complete Test Suite**: Implement comprehensive unit, integration (API <> Backend, Service <> DB), and end-to-end tests. Add security-focused tests (input validation, auth checks). Achieve high test coverage.
2. **Enhance Email Campaign Tracking**: Implement open/click/response tracking mechanisms. Develop detailed performance reporting and analytics.
3. **Complete n8n Workflow Integration**: Refine existing workflows, improve error handling within n8n, create documentation for workflow usage, enhance proposal matching logic if needed.

### PRIORITY 4: Strategic Expansion & Security Hardening
1. **Further Security Enhancements**: Implement comprehensive database security (parameterized queries everywhere, audit logging, transactions). Conduct dependency vulnerability scanning (pip-audit). Add more granular authorization checks.
2. **Create Comprehensive Documentation**: Write detailed user guides, API documentation, deployment guides, and troubleshooting information.
3. **Future Consideration (Post-Stabilization)**: Evaluate expanding the scope (e.g., global data sources) based primarily on the availability and feasibility of reliable API data sources in new regions.

## MCP-Powered Apify Integration

The integration of MCP-powered Apify Actors provides a breakthrough solution for reliable data acquisition:

### Data Sources

1. **Google Maps Proxy (gmaps-proxy)**
   - Provides access to thousands of Malaysian businesses with accurate contact information
   - Contains location data, phone numbers, websites, and ratings
   - Allows targeting by business category and geographic area
   - Offers reliable, structured data with minimal processing required

2. **Instagram Scraper**
   - Extracts business information from Instagram profiles
   - Provides insights into social media presence and engagement
   - Offers additional contact points and business descriptions
   - Enables targeting based on hashtags and location tags

3. **RAG Web Browser**
   - Combines Google search with website content extraction
   - Provides clean, structured content from business websites
   - Bypasses anti-scraping measures through Apify infrastructure
   - Enables targeted research for specific business information

### Implementation Approach

The integration follows an adapter pattern to standardize responses:

1. **Client Classes**
   - Each MCP-powered Actor has a dedicated client class
   - Clients handle authentication, rate limiting, and error handling
   - Responses are standardized to fit our Lead model
   - Caching is implemented to minimize API calls

2. **Data Standardization**
   - Common fields are mapped across all sources
   - Source-specific fields are preserved for enrichment
   - Validation ensures data quality and consistency
   - Deduplication prevents redundant entries

3. **Multi-Source Enrichment**
   - Primary lookup via Google Maps
   - Secondary enrichment from Instagram profiles
   - Tertiary enrichment from website content
   - Intelligent matching based on business name and location

4. **Lead Scoring**
   - Quality scores based on data completeness
   - Targeting suitability based on business category
   - Engagement potential based on social media presence
   - Proposal matching based on business characteristics

### Benefits

1. **Reliability**: Production-grade infrastructure managed by Apify
2. **Scalability**: Can handle large volumes of requests
3. **Data Quality**: Rich, structured data with minimal processing required
4. **Flexibility**: Multiple data sources for comprehensive business profiles
5. **Efficiency**: Minimal development effort compared to building custom scrapers

## n8n Workflow Automation Integration

The n8n integration will be updated to leverage the new MCP-powered data sources:

### Current Implementation

The integration includes the following components:

1. **API Service Layer**
   - `api_service.py`: Connects API endpoints with core functionality
   - Methods for lead management, email generation, and dashboard statistics
   - Error handling and logging mechanisms

2. **Database Enhancements**
   - `DashboardStats` model for analytics tracking
   - Extended `LeadStatus` enumeration
   - Relationship tracking between models

3. **API Routes**
   - FastAPI endpoints for leads, emails, and dashboard statistics
   - Authentication and permission checking
   - Error handling and validation

4. **n8n Workflows**
   - Lead acquisition workflow using MCP-powered data sources (NEW)
   - Email generation workflow with template selection
   - Email sending workflow with rate limiting and tracking
   - Email sending with proposals workflow for attachment handling
   - Analytics workflow with custom reporting

5. **Security Measures**
   - JWT-based authentication for API access
   - Secure credential storage in n8n
   - Role-based permission system
   - Rate limiting to prevent abuse
   - Input validation with Pydantic models

### Setting Up n8n Integration

1. **Install API Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Install n8n**
   ```
   npm install n8n -g
   ```

3. **Start the API Server**
   ```
   run_api.bat
   ```

4. **Start n8n**
   ```
   n8n start
   ```

5. **Import Workflows**
   - Navigate to n8n at http://localhost:5678/
   - Go to Workflows > Import From File
   - Import each workflow JSON file from the n8n_workflows directory
   - Configure credentials for the API connection

## Security Enhancements

We've significantly improved the security posture of the Malaysian Lead Generator project:

### API Security
- Replaced wildcard CORS settings with specific allowed origins
- Added comprehensive rate limiting based on client IP addresses
- Implemented request logging for security monitoring
- Added secure error handling that prevents information leakage
- Enhanced authentication with secure token generation

### Input Validation
- Created extensive Pydantic models for all API inputs
- Added validators for email addresses, phone numbers, and URLs
- Implemented sanitization to prevent injection attacks
- Added validation for file paths to prevent path traversal attacks
- Enhanced validation for proposal attachment handling

### Configuration Security
- Eliminated hardcoded secrets and replaced with environment variables
- Added automatic secret generation with appropriate warnings
- Improved token expiration with configurable timeouts
- Secure storage for Apify API credentials

These security enhancements bring the codebase in line with production-grade standards, following a defense-in-depth approach with multiple layers of protection.

---
*Last updated: June 10, 2024*

# Agentive Frontend Integration Roadmap

**Note**: This frontend development is now Priority 2 in the project plan and can proceed immediately as the data acquisition issue has been resolved with MCP-powered Apify Actors.

## Separation of Concerns

The integration follows a clear separation of concerns:

1. **Backend (Python)**
   - Core business logic
   - Data processing and storage
   - Email generation and sending
   - Multi-source data acquisition via MCP-powered Apify Actors

2. **Frontend (Agentive)**
   - User interface and experience
   - Visualization and reporting
   - Interactive workflows
   - User management and permissions

## Implementation Plan

The implementation can now proceed immediately:

1. **API Layer Enhancement** (Completed - additional updates for new data sources required)
   - Extend existing FastAPI routes to support all frontend needs
   - Implement comprehensive authentication and authorization
   - Add pagination, filtering, and sorting capabilities
   - Ensure proper error handling and validation
   - Add endpoints for the new data sources

2. **User Interface Development** (Current Priority - Phase 2)
   - Create responsive dashboard layout
   - Implement lead management interfaces
   - Build email campaign management screens
   - Design analytics and reporting visualizations
   - Develop user and permission management
   - Add data source visualization and filtering

3. **Workflow Integration within UI**
   - Create guided workflows for common tasks
   - Implement drag-and-drop email template customization
   - Add proposal attachment selection interface
   - Build campaign scheduling and tracking tools
   - Create data source selection and enrichment interfaces

4. **Testing and Optimization**
   - Conduct usability testing
   - Optimize performance for larger datasets
   - Ensure mobile compatibility
   - Implement accessibility features

## Benefits

The Agentive Frontend integration will provide several key benefits:

1. **Increased Usability**
   - No technical knowledge required for basic operations
   - Intuitive interfaces for common tasks
   - Visual workflows and guidance
   - Multi-source data visualization

2. **Enhanced Collaboration**
   - Multi-user support with role-based permissions
   - Shared dashboards and reports
   - Collaborative campaign management
   - Centralized lead database

3. **Improved Visualization**
   - Interactive data visualizations
   - Real-time performance metrics
   - Custom reports and exports
   - Lead quality scoring visualization

4. **Streamlined Workflows**
   - Guided processes for common tasks
   - Drag-and-drop customization
   - Template management and reuse
   - Intelligent proposal matching

## Additional Requirements

The Agentive Frontend integration will require:

1. **Dependencies**
   - Modern frontend framework
   - Charting and visualization libraries
   - Authentication and authorization components
   - Form validation and handling
   - Data filtering and search capabilities

2. **Infrastructure**
   - Web server for hosting frontend
   - Proxy configuration for API communication
   - Secure HTTPS connections
   - User session management
   - Integration with MCP-powered data sources 