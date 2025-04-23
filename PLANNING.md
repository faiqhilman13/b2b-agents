# Malaysian Lead Generator Project Planning

## Project Overview
The Malaysian Lead Generator is a tool designed to collect business contacts primarily through reliable API data sources, supplemented with targeted web scraping, and generate personalized outreach emails. The system provides secure handling of credentials, flexible templating for emails, and various delivery options including intelligent PDF proposal selection and attachment.

## Architecture

### Core Components
1. **Lead Collection**
   - API-based data acquisition (primary)
     - Integration with business data providers
     - Open data source utilization
     - Standardized data processing pipeline
   - Targeted web scraping for enrichment (secondary)
     - Limited scope for specific high-value targets
     - Advanced anti-blocking mechanisms when necessary
     - Selective data enrichment

2. **Email Generation**
   - Template-based email creation
   - Personalization with dynamic variables
   - Template selection based on lead source and characteristics

3. **Email Sending**
   - SMTP integration with rate limiting
   - Intelligent PDF proposal selection and attachment
   - Batch processing with retries and error handling

4. **Security**
   - Credential encryption using industry-standard methods
   - Secure vault for sensitive information
   - Environment variable management
   - Input validation and sanitization
   - Specific CORS configurations

5. **API Layer**
   - FastAPI-based REST endpoints
   - JWT authentication and permission-based access control
   - Pydantic models for validation
   - Rate limiting and security middleware

6. **n8n Workflow Automation**
   - Workflow templates for common tasks
   - Integration with core services
   - Visual automation capabilities

7. **Agentive Frontend** (Planned)
   - User-friendly web interface
   - Dashboard for analytics
   - Lead and campaign management

### File Structure
```
/
├── lead_generator/            # Main package
│   ├── agents/                # Core functionality modules
│   │   ├── api_clients/       # API-based data acquisition (to be implemented)
│   │   │   ├── base_client.py # Base API client functionality
│   │   │   ├── clearbit.py    # Example API integration
│   │   │   ├── opencorporates.py # Example API integration
│   │   ├── scrapers/          # Targeted enrichment scrapers
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
│   │   ├── middleware.py      # Rate limiting and security middleware
│   │   ├── models.py          # Pydantic validation models
│   ├── config/                # Configuration files
│   │   ├── email_config.py    # Email settings
│   │   ├── secure_config.py   # Secure credential management
│   │   ├── proposal_config.py # Proposal selection configuration
│   │   ├── api_config.py      # API client configurations (to be implemented)
│   ├── database/              # Database models and queries
│   │   ├── models.py          # SQLite schema definitions
│   │   ├── queries.py         # Database operation functions
│   ├── prompts/               # Email templates
│   │   ├── default.json       # Various email templates
│   ├── utils/                 # Utility functions
│   │   ├── cache.py           # Deduplication and tracking
│   │   ├── email_validator.py # Email validation
│   │   ├── data_processor.py  # Data standardization (to be implemented)
│   ├── tests/                 # Test suites
│       ├── unit/              # Unit tests
│       │   ├── test_api_clients.py # Tests for API integrations (to be implemented)
│       │   ├── test_scrapers.py
│       │   ├── test_email_sender.py
├── n8n_workflows/             # n8n workflow exports
├── proposals/                 # PDF proposal storage
├── scripts/                   # Utility scripts
├── .env.template              # Template for environment variables
```

## Coding Standards

### General Standards
- **Python Version**: Python 3.8+ compatible
- **Code Style**: PEP8 compliant with proper type hints
- **Documentation**: Google-style docstrings for all functions and classes
- **File Structure**: Maximum of 500 lines per file; longer files should be split
- **Module Organization**: Group related functionality within packages

### Naming Conventions
- **Files**: Snake case (e.g., `email_sender.py`)
- **Classes**: Pascal case (e.g., `EmailSender`)
- **Functions/Methods**: Snake case (e.g., `send_email`)
- **Variables**: Snake case (e.g., `email_config`)
- **Constants**: Upper case with underscores (e.g., `EMAIL_RATE_LIMIT`)

### Import Conventions
- Group imports in this order: stdlib, third-party, project
- Use relative imports within packages
- Avoid wildcard imports (`from x import *`)

### Error Handling
- Use specific exception types
- Always log exceptions with context
- Implement proper retry mechanisms for external services
- Provide clear error messages for end users

### Security Practices
- Use parameterized queries for all database operations
- Validate all inputs, especially those from external sources
- Store sensitive data in the encrypted credential vault
- Follow the principle of least privilege
- Implement proper rate limiting for all external-facing endpoints
- Sanitize inputs to prevent injection attacks
- Lock down CORS settings in production to specific origins
- Always use HTTPS in production
- Audit logging for sensitive operations

## Testing Strategy

### Unit Testing
- **Framework**: PyTest
- **Coverage**: Aim for 80%+ code coverage
- **Mocking**: Use unittest.mock for external services
- **Test Types**:
  - Expected use cases
  - Edge cases
  - Failure cases

### Integration Testing
- Test interactions between components
- Verify API endpoint behavior
- Test database operations with a test database
- Test API client integrations with mock responses

### Security Testing
- Regular credential rotation
- Input validation testing
- Authentication and authorization testing
- Rate limiting verification
- API client authentication testing

## API Integration Requirements
- Evaluate and document API rate limits and quotas
- Store API credentials securely
- Implement request caching to minimize API calls
- Handle API errors gracefully with appropriate retries
- Standardize data formats from different API sources
- Implement proper API client tests with mock responses

## Performance Constraints
- Email sending rate limit: 100 emails per hour
- Maximum attachment size: 10MB
- API response time: <500ms for most endpoints
- API client request timeout: configurable per provider

## Deployment Guidelines
- Environment variable configuration
- Secure credential management
- Proper permissions for sensitive directories
- Regular backup procedures
- Monitoring and alerting setup

## Dependency Management
- Use requirements.txt with pinned versions
- Minimize third-party dependencies
- Regular security updates
- Documentation for all dependencies

## Documentation Requirements
- README.md for project overview
- SECURITY.md for security guidelines
- API documentation
- Setup and deployment guides
- User documentation for email templates and workflow
- API client documentation and setup procedures

## Task Management
- Track all tasks in TASK.md
- Mark completed tasks promptly
- Document discovered tasks under "Discovered During Work"
- Include deadlines for critical tasks 