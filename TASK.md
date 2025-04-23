# Malaysian Lead Generator Project Tasks

## Active Tasks

### Data Acquisition Pivot (HIGHEST PRIORITY - Added 2024-06-05)
- [ ] Research and evaluate API-based data sources for Malaysian business contacts
  - [ ] Investigate Clearbit, Apollo, OpenCorporates, local government APIs
  - [ ] Evaluate coverage, quality, cost, and terms of service
  - [ ] Document findings and select 1-2 promising sources
- [ ] Implement API client infrastructure
  - [ ] Create base API client class with authentication and error handling
  - [ ] Implement request caching and rate limiting
  - [ ] Add credential management for API keys
- [ ] Develop proof-of-concept integrations
  - [ ] Implement integration with primary selected API
  - [ ] Create data standardization module
  - [ ] Test API responses and handle edge cases
- [ ] Adjust database models for API-sourced data
  - [ ] Update Lead model with new fields for API metadata
  - [ ] Add source tracking and enrichment fields
  - [ ] Create migration path for existing data
- [ ] Re-evaluate scraping for targeted enrichment
  - [ ] Select one specific high-value scraping target
  - [ ] Implement advanced anti-blocking using Playwright or Selenium
  - [ ] Test feasibility and make go/no-go decision on scraping
- [ ] Update workflow with API data sources
  - [ ] Refactor main.py to prioritize API-based acquisition
  - [ ] Update n8n workflows for API-first approach
  - [ ] Ensure smooth operation of email generation with API data

### Security Improvements
- [x] Implement stronger CORS settings in API layer
- [x] Add rate limiting for all API endpoints
- [x] Enhance input validation using Pydantic models
- [x] Add sanitization for all user inputs
- [x] Strengthen authentication with longer token expiration controls
- [ ] Implement parameterized queries across all database operations
- [x] Add generic error responses in production mode
- [ ] Implement audit logging for sensitive operations
- [ ] Secure API key storage and management for external services

### Agentive Frontend (Contingent on Data Acquisition Pivot)
- [ ] Design user-friendly web interface
- [ ] Implement dashboard for analytics
- [ ] Create lead management interface
- [ ] Build email template management system
- [ ] Implement proposal management interface

### Testing Enhancements
- [ ] Complete unit tests for email generation module
- [ ] Add integration tests for API endpoints
- [ ] Create tests for API client integrations
- [ ] Implement end-to-end tests for main workflows
- [ ] Add security-focused tests for authentication and authorization

## Deprioritized Tasks

### Scraper Functionality (Deprioritized in favor of API-first approach)
- [ ] Fix recurring 403 Forbidden errors on BusinessList.my and YellowPages.my
- [ ] Implement proxy rotation for scraping
- [ ] Add more realistic browser fingerprinting
- [ ] Implement exponential backoff for failed requests

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

*Last updated: 2024-06-05* 