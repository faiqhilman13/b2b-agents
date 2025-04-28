# Malaysian Lead Generator Project Tasks

## Active Tasks

### MCP-Powered Apify Integration (HIGHEST PRIORITY - Added 2024-06-10)
- [x] Integrate MCP-powered Apify Actors for reliable data acquisition
  - [x] Create GoogleMapsClient adapter for gmaps-proxy
  - [x] Create InstagramClient adapter for instagram-scraper
  - [x] Create WebBrowserClient adapter for rag-web-browser
  - [x] Implement unified data standardization pipeline
  - [x] Add caching to minimize API calls
- [x] Enhance database models for rich API data
  - [x] Add social media profile fields (Instagram)
  - [x] Add location and rating fields (Google Maps)
  - [x] Add data source tracking and timestamp fields
  - [x] Create migration path for existing data
- [x] Update workflow to leverage new data sources
  - [x] Refactor main.py to prioritize MCP-powered data sources
  - [x] Update n8n workflows for multi-source enrichment
  - [x] Adjust email templates for new data points
  - [x] Create targeting strategy based on business categories
- [ ] Implement multi-source lead enrichment
  - [x] Create lead enrichment pipeline combining data from multiple sources
  - [ ] Implement lead scoring based on data completeness
  - [x] Develop intelligent proposal matching using enhanced data
  - [x] Add validation and deduplication for multi-source data

### Frontend-Backend Integration (HIGH PRIORITY - Added 2024-07-06)
- [x] Setup API service layer in frontend
  - [x] Create API client service with axios/fetch
  - [x] Implement authentication interceptors
  - [x] Add error handling and response normalization
  - [x] Create API endpoints for all required data operations
- [x] Implement authentication flow
  - [x] Create login/register components
  - [x] Implement JWT token management
  - [x] Add protected routes with authentication guards
  - [x] Create user context provider
- [ ] Connect frontend components to backend API
  - [x] Update dashboard to display real data
  - [x] Connect lead management page to leads API
  - [ ] Link campaign management to campaign API endpoints
  - [ ] Connect proposal management UI to backend
- [x] Implement data management features
  - [x] Add pagination, filtering, and sorting for data tables
  - [x] Create search functionality across leads and campaigns
  - [x] Implement form validation with error handling
  - [x] Add optimistic UI updates with error rollback
- [ ] Enhance security measures
  - [x] Implement proper CORS configuration
  - [x] Add CSRF protection
  - [x] Sanitize user inputs
  - [ ] Set up proper HTTP-only cookie handling
- [ ] Create documentation
  - [ ] Document API integration for frontend developers
  - [ ] Add examples for common data operations
  - [ ] Document authentication flow and security measures
  - [ ] Create component documentation for the frontend

### Data Acquisition Pivot (Completed 2024-06-10)
- [x] Research and evaluate API-based data sources for Malaysian business contacts
  - [x] Selected MCP-powered Apify Actors as primary data source
  - [x] Evaluated coverage, quality, and terms of service
  - [x] Documented capabilities of Google Maps, Instagram, and RAG Web Browser
- [x] Identify API client infrastructure requirements
  - [x] Determined need for adapter pattern to standardize responses
  - [x] Identified caching requirements to optimize API usage
  - [x] Documented authentication and error handling needs

### Security Improvements
- [x] Implement stronger CORS settings in API layer
- [x] Add rate limiting for all API endpoints
- [x] Enhance input validation using Pydantic models
- [x] Add sanitization for all user inputs
- [x] Strengthen authentication with longer token expiration controls
- [ ] Implement parameterized queries across all database operations
- [x] Add generic error responses in production mode
- [ ] Implement audit logging for sensitive operations
- [x] Secure API key storage and management for external services
- [x] Add secure handling for Apify API credentials

### Testing Enhancements
- [ ] Complete unit tests for email generation module
- [ ] Add integration tests for API endpoints
- [x] Create tests for API client integrations (Google Maps client)
- [x] Create tests for InstagramClient adapter
- [ ] Implement end-to-end tests for main workflows
- [ ] Add security-focused tests for authentication and authorization
- [ ] Create tests for additional MCP-powered Apify client adapters
- [ ] Create frontend component tests with React Testing Library
- [ ] Add integration tests for frontend-backend communication
- [ ] Implement end-to-end testing with Cypress

## Deprioritized Tasks

### Legacy Scraper Functionality (Deprecated in favor of MCP-powered approach)
- [x] Replace unreliable web scraping with MCP-powered Apify Actors


## Completed Tasks

### Project Structure Reorganization (Completed 2024-04-14)
- [x] Reorganize project into proper Python package structure
- [x] Move files to appropriate directories according to PLANNING.md
- [x] Create missing __init__.py files
- [x] Update scripts to work with new structure
- [x] Update imports to reflect new structure
- [x] Remove duplicated files and clean up project structure

### Core Functionality
- [x] Implement Yellow Pages scraper (to be repurposed for targeted enrichment)
- [x] Implement Government ministry scraper (to be repurposed for targeted enrichment)
- [x] Implement University website scraper (to be repurposed for targeted enrichment)
- [x] Create email generation system
- [x] Build email sending functionality
- [x] Add PDF proposal attachment support
- [x] Implement package-based proposal selection

### Security & Compliance
- [x] Create secure credential management
- [x] Implement credential encryption
- [x] Add environment variable support
- [x] Create secure configuration hierarchy
- [x] Document security best practices in SECURITY.md

### API & Integration
- [x] Develop API service layer
- [x] Create FastAPI endpoints
- [x] Implement JWT authentication
- [x] Add permission-based authorization
- [x] Develop n8n workflow templates

### Frontend Development (Added 2024-07-06)
- [x] Set up React.js frontend with Vite and TypeScript
- [x] Create responsive UI components with Tailwind CSS
- [x] Implement theme switching (light/dark mode)
- [x] Build authentication UI with login/logout
- [x] Create protected route system
- [x] Build lead management interface

### Maintenance
- [x] Create cleanup utilities for temporary files
- [x] Implement import fixing utility
- [x] Add test data generator
- [x] Create command-line interface and batch scripts

## Discovered During Work
- [ ] Need comprehensive error reporting system for production
- [ ] Email tracking pixel capability needed
- [ ] Consider serverless deployment option for better scaling
- [ ] Evaluate the need for a standalone proxy service for API reliability
- [ ] Explore additional Apify Actors for data enrichment
- [ ] Consider implementing AI-based lead qualification using gathered data
- [x] Fix logging consistency in API client modules (use logger instance instead of direct logging module)
- [x] Create client activation mechanism to fully enable MCP Actor integration in __init__.py
- [x] Add documentation for API client usage and configuration
- [x] Implement custom exception classes for API client errors
- [x] Create frontend services directory for API integration (discovered 2024-07-06)
- [ ] Implement token refresh mechanism to handle expired JWT tokens (discovered 2024-07-06)
- [x] Need to update API CORS settings to allow frontend origin (discovered 2024-07-06)
- [x] Create error boundary components for frontend error handling (discovered 2024-07-06)
- [ ] Setup development environment documentation for new team members (discovered 2024-07-07)
- [ ] Fix backend FastAPI startup issues with Python 3.13 compatibility (discovered 2024-07-07)
- [ ] Document frontend-backend API contracts for consistent development (discovered 2024-07-07)
- [ ] Create Docker compose setup for easier development environment (discovered 2024-07-07)

*Last updated: 2024-07-10* 