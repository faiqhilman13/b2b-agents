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

Lead Collection (Phase 1) infrastructure (scrapers, CLI integration) exists but faces significant reliability challenges.

Initial progress on the Agentive Frontend Integration (Phase 8) API foundation is complete, but UI development is pending.

**Important Note:** While the surrounding infrastructure (API, email logic, n8n workflows, security) is robust and functions correctly with test data, the core challenge remains reliable lead acquisition. The original web scraping approach faces persistent blocking and parsing issues. Therefore, the immediate top priority is pivoting the data acquisition strategy towards more reliable API-based sources, using scraping techniques primarily for targeted enrichment where feasible.

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
│   │   ├── .secure/           # Encrypted credential storage (not in VCS)
│   ├── database/              # Database models and queries
│   │   ├── models.py          # SQLite schema definitions
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
│   ├── tests/                 # Test suites
│   │   ├── unit/
│   │       ├── test_scrapers.py
│   │       ├── test_email_sender.py  # Email sender tests
│   │       ├── test_email_generator.py
│   ├── main.py                # Main entry point for CLI
├── scripts/                   # Utility scripts
│   ├── run_lead_generator.bat # Script to run the lead generator
│   ├── run_api.bat            # Script to run the API server
│   ├── run_scraper.bat        # Legacy batch script (to be updated)
│   ├── cleanup_temp_files.py  # Utility for cleaning temporary files
│   ├── cleanup_temp_files.bat # Batch file for cleanup operations
│   ├── fix_imports.py         # Utility to fix import statements
├── proposals/                 # Directory for PDF proposal files
├── n8n_workflows/             # Directory containing n8n workflow exports
│   ├── lead_scraping.json     # Lead scraping workflow (To be refocused on API/Enrichment)
│   ├── email_generation.json  # Email generation workflow
│   ├── email_sending.json     # Email sending workflow
│   ├── email_sending_with_proposals.json  # Email sending with PDF attachments workflow
│   ├── analytics.json         # Analytics and reporting workflow
├── output/                    # Output directory for scraped data
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

### Lead Collection Phase (Infrastructure COMPLETED, Data Acquisition PARTIALLY COMPLETED)
1. ✅ Implemented multiple scrapers (YellowPages, Gov, Uni)
2. ✅ Added basic anti-blocking measures (delays, headers)
3. ✅ Implemented basic contact extraction strategies
4. ✅ Created command-line interface and batch scripts for scraping
5. ✅ Added logging and error handling for scraping
6. ❌ (MAJOR ISSUE) Ongoing issues with reliable scraping (403s, parsing errors)

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
- **Major Data Acquisition Issues**:
  - Core Problem: The current web scraping approach is unreliable and fails frequently (403s, parsing errors) against real-world targets.
  - Low success rate of obtaining valid business contacts via scraping.
  - Workflow functions correctly with test data but lacks reliable real data input.
- n8n integration requires separate setup.
- **Incomplete Test Suite**: Missing comprehensive unit, integration, and end-to-end tests.
- **Web Frontend Not Implemented**: System currently relies on CLI/batch files and n8n UI.

## Next Steps (Revised Priorities)

### PRIORITY 1: Data Acquisition Pivot & Stabilization (HIGHEST PRIORITY)
1. **Research & Identify Reliable Data Sources**: Aggressively investigate API providers (e.g., Clearbit, Apollo, OpenCorporates, relevant government APIs) and reliable open data sources for Malaysian business information. Evaluate coverage, quality, cost, and terms of service.
2. **Implement API Integrations (POC)**: Select 1-2 promising API sources and build proof-of-concept integrations to fetch base lead data reliably.
3. **Refactor Backend for API-First**: Adjust database models (database/models.py) and core logic to primarily handle data ingested from APIs. Define fields for potential enrichment data.
4. **Re-evaluate Scraping (Targeted Enrichment Only)**:
   - Select one specific scraping target where enrichment data might be valuable and potentially feasible.
   - Experiment with one advanced technique (e.g., Playwright/Selenium with rotating residential proxies) as a POC strictly for enrichment.
   - If POC fails or proves too costly/unreliable, significantly deprioritize or remove scraping efforts.
5. **Stabilize Core Workflow with API Data**: Ensure the entire existing pipeline (DB storage, email generation, proposal matching, n8n workflows) functions smoothly using data acquired via APIs. Update n8n_workflows/lead_scraping.json to reflect the API-first approach.

### PRIORITY 2: Agentive Frontend Integration (UI Development)
(Contingent on successful data acquisition in Priority 1)
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

## n8n Workflow Automation Integration
(This section remains largely the same as it describes the completed integration, but the context now assumes data primarily comes from APIs)

The n8n integration has been completed, providing a powerful workflow automation platform while preserving the robust Python backend for core functionality. This approach offers the best of both worlds: a powerful backend with flexible, visual workflow automation.

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
   - Lead scraping workflow with scheduling options (to be refocused on API/Enrichment)
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

These security enhancements bring the codebase in line with production-grade standards, following a defense-in-depth approach with multiple layers of protection.

---
*Last updated: June 5, 2025*

# Agentive Frontend Integration Roadmap

**Note**: This frontend development is now Priority 2 in the project plan, to be commenced after the successful pivot to reliable API-based data acquisition (Priority 1).

## Separation of Concerns

The integration follows a clear separation of concerns:

1. **Backend (Python)**
   - Core business logic
   - Data processing and storage
   - Email generation and sending
   - API-based lead acquisition with targeted web scraping enrichment

2. **Frontend (Agentive)**
   - User interface and experience
   - Visualization and reporting
   - Interactive workflows
   - User management and permissions

## Implementation Plan

The implementation will proceed after Priority 1 is substantially complete:

1. **API Layer Enhancement** (Completed - verification may be needed post-Priority 1 refactor)
   - Extend existing FastAPI routes to support all frontend needs
   - Implement comprehensive authentication and authorization
   - Add pagination, filtering, and sorting capabilities
   - Ensure proper error handling and validation

2. **User Interface Development** (Current Priority - Phase 2)
   - Create responsive dashboard layout
   - Implement lead management interfaces
   - Build email campaign management screens
   - Design analytics and reporting visualizations
   - Develop user and permission management

3. **Workflow Integration within UI**
   - Create guided workflows for common tasks
   - Implement drag-and-drop email template customization
   - Add proposal attachment selection interface
   - Build campaign scheduling and tracking tools

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

2. **Enhanced Collaboration**
   - Multi-user support with role-based permissions
   - Shared dashboards and reports
   - Collaborative campaign management

3. **Improved Visualization**
   - Interactive data visualizations
   - Real-time performance metrics
   - Custom reports and exports

4. **Streamlined Workflows**
   - Guided processes for common tasks
   - Drag-and-drop customization
   - Template management and reuse

## Additional Requirements

The Agentive Frontend integration will require:

1. **Dependencies**
   - Modern frontend framework
   - Charting and visualization libraries
   - Authentication and authorization components
   - Form validation and handling

2. **Infrastructure**
   - Web server for hosting frontend
   - Proxy configuration for API communication
   - Secure HTTPS connections
   - User session management 