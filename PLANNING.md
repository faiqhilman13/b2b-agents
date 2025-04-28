# Malaysian Lead Generator Project Planning

## Project Overview
The Malaysian Lead Generator is a tool designed to collect business contacts primarily through reliable API data sources, supplemented with targeted web scraping, and generate personalized outreach emails. The system provides secure handling of credentials, flexible templating for emails, and various delivery options including intelligent PDF proposal selection and attachment.

## Getting Started

### Running the Application
To run the application locally for development:

1. **Start the frontend**:
   ```
   cd frontend
   npm install   # Only needed first time or when dependencies change
   npm run dev   # Starts the development server
   ```
   The frontend will be accessible at http://localhost:5173 or http://localhost:5174

2. **Start the backend**:
   ```
   cd lead_generator/api
   python -m uvicorn app:app --reload
   ```
   The API will be accessible at http://localhost:8000

### Dependencies
- **Frontend**: React.js, TypeScript, Vite, Tailwind CSS, Chart.js, Axios
- **Backend**: Python 3.8+, FastAPI, Uvicorn, SQLite, Python-jose, Python-multipart, Pydantic

## Architecture

### Core Components
1. **Lead Collection**
   - MCP-Powered Apify Actors (primary)
     - Google Maps Proxy for business location and contact data
     - Instagram Scraper for social media profile extraction
     - RAG Web Browser for website content extraction
     - Standardized data processing pipeline
   - Targeted web scraping for enrichment (secondary/deprecated)
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

7. **Agentive Frontend**
   - User-friendly React.js web interface
   - Dashboard for analytics and visualization
   - Lead and campaign management
   - Secure authentication with JWT
   - Responsive design with Tailwind CSS

8. **Frontend-Backend Integration**
   - API service layer for data communication
   - State management with React Context API
   - Secure authentication flow
   - Optimistic UI updates for improved UX
   - Error handling and retry mechanisms

### File Structure
```
/
├── lead_generator/            # Main package
│   ├── agents/                # Core functionality modules
│   │   ├── api_clients/       # API-based data acquisition
│   │   │   ├── base_client.py # Base API client functionality
│   │   │   ├── gmaps_client.py # Google Maps integration (IMPLEMENTED)
│   │   │   ├── instagram_client.py   # Instagram integration (IN PROGRESS)
│   │   │   ├── web_browser_client.py # RAG Web Browser integration (IMPLEMENTED)
│   │   ├── scrapers/          # Legacy scrapers (deprecated)
│   │   │   ├── scraper.py     # Base scraper functionality
│   │   │   ├── yellow_pages_scraper.py
│   │   │   ├── gov_ministry_scraper.py
│   │   │   ├── university_scraper.py
│   │   ├── email_generator.py
│   │   ├── email_sender.py
│   │   ├── api/                   # API layer
│   │   │   ├── api_service.py     # API service connecting to core functions
│   │   │   ├── auth.py            # Authentication functions
│   │   │   ├── routes.py          # API route definitions
│   │   │   ├── app.py             # FastAPI application
│   │   │   ├── middleware.py      # Rate limiting and security middleware
│   │   │   ├── models.py          # Pydantic validation models
│   │   ├── config/                # Configuration files
│   │   │   ├── email_config.py    # Email settings
│   │   │   ├── secure_config.py   # Secure credential management
│   │   │   ├── proposal_config.py # Proposal selection configuration
│   │   │   ├── api_config.py      # API credentials and configuration
│   │   ├── database/              # Database models and queries
│   │   │   ├── models.py          # SQLite schema definitions
│   │   │   ├── queries.py         # Database operation functions
│   │   ├── prompts/               # Email templates
│   │   │   ├── default.json       # Various email templates
│   │   ├── utils/                 # Utility functions
│   │   │   ├── cache.py           # Deduplication and tracking
│   │   │   ├── email_validator.py # Email validation
│   │   │   ├── data_processor.py  # Data standardization
│   │   ├── tests/                 # Test suites
│   │   │   ├── unit/              # Unit tests
│   │   │   │   ├── test_api_clients.py # Tests for API integrations
│   │   │   │   ├── test_scrapers.py
│   │   │   │   ├── test_email_sender.py
│   │   ├── n8n_workflows/             # n8n workflow exports
│   │   ├── proposals/                 # PDF proposal storage
│   │   ├── scripts/                   # Utility scripts
│   │   ├── .env.template              # Template for environment variables
│   │   └── frontend/                  # React.js based frontend
│   │       ├── src/                   # Frontend source code
│   │       │   ├── components/        # Reusable UI components
│   │       │   ├── context/           # React context providers
│   │       │   ├── pages/             # Page components
│   │       │   ├── services/          # API service integrations
│   │       │   ├── hooks/             # Custom React hooks
│   │       │   ├── utils/             # Utility functions
│   │       │   ├── App.tsx            # Main application component
│   │       │   ├── main.tsx           # Application entry point
│   │       └── public/                # Static assets
│   │           ├── package.json           # Frontend dependencies
│   │           ├── tsconfig.json          # TypeScript configuration
│   │           └── vite.config.ts         # Vite build configuration
│   │           └── index.html             # HTML entry point
```

## MCP-Powered Apify Actor Integration Status
The integration of MCP-powered Apify Actors is our current highest priority. Here's the current status:

### Completed
- Base API client framework with caching, rate limiting, and error handling
- Google Maps client adapter (gmaps-proxy)
  - Business search functionality
  - Place details retrieval
  - Location-based search
  - Data standardization to lead format
  - Unit tests
- RAG Web Browser client adapter
  - Search and content extraction
  - URL-specific content extraction
  - Business contact extraction from content
  - Data standardization to lead format

### In Progress
- Instagram client adapter (instagram-scraper)
  - Profile details retrieval
  - Profile posts extraction
  - Business contact information extraction
  - Data standardization to lead format
- Unified data standardization pipeline
- Client activation mechanism in __init__.py

### Upcoming
- Multi-source lead enrichment pipeline
- Database model enhancements
- Workflow integration
- Additional unit and integration tests

## Frontend-Backend Integration

### Authentication Flow
1. **User Authentication**
   - Login via JWT token-based authentication
   - Token storage in secure HTTP-only cookies
   - Token refresh mechanism
   - Session management
   - Role-based access control

2. **API Integration**
   - Centralized API service layer
   - Request interceptors for authentication
   - Response handling and error normalization
   - Caching strategies for improved performance
   - Rate limiting awareness

3. **State Management**
   - React Context API for global state
   - Local component state for UI interactions
   - Optimistic UI updates for improved user experience
   - Form state management

### Data Flow
1. **Data Fetching**
   - Paginated data loading
   - Search and filtering parameters
   - Sorting and ordering
   - Data transformation adapters
   - Caching and stale-while-revalidate patterns

2. **Data Submission**
   - Form validation with client-side schema validation
   - Optimistic updates with rollback on error
   - Progress indicators for long-running operations
   - Error handling and user feedback

### Security Considerations
1. **Frontend Security**
   - Protection against XSS via proper content sanitization
   - CSRF protection via tokens
   - Content Security Policy implementation
   - Secure cookie handling
   - Input validation
   - Avoid exposing sensitive information in client-side code

2. **API Security**
   - JWT token validation
   - Rate limiting for API endpoints
   - CORS configuration to allow only the frontend origin
   - Input sanitization and validation
   - Specific error messages that don't leak implementation details

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

### Frontend Standards
- **TypeScript**: Use TypeScript for type safety
- **Component Structure**: Functional components with hooks
- **Styling**: Tailwind CSS for responsive design
- **Code Splitting**: Lazy loading for improved performance
- **Error Handling**: Proper error boundaries and fallbacks
- **Accessibility**: WCAG 2.1 AA compliance

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

### Frontend Testing
- Component testing with React Testing Library
- End-to-end testing with Cypress
- Visual regression testing
- Accessibility testing

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

### MCP-Powered Apify Actor Integration
- Store Apify credentials securely in credential vault
- Implement adapter pattern for standardizing responses
- Add caching to optimize API usage
- Create multi-source enrichment pipeline
- Establish data quality validation process
- Ensure error handling and retries for reliability

## Performance Constraints
- Email sending rate limit: 100 emails per hour
- Maximum attachment size: 10MB
- API response time: <500ms for most endpoints
- API client request timeout: configurable per provider
- MCP-powered Actor request budget: optimize for cost-effectiveness
- Frontend initial load time: <2s for critical content
- Time to interactive: <3s on average connections

## Deployment Guidelines
- Environment variable configuration
- Secure credential management
- Proper permissions for sensitive directories
- Regular backup procedures
- Monitoring and alerting setup
- Frontend/backend deployment coordination
- Staged deployment process

## Dependency Management
- Use requirements.txt with pinned versions
- Minimize third-party dependencies
- Regular security updates
- Documentation for all dependencies
- Frontend dependency audit and updates

## Documentation Requirements
- README.md for project overview
- SECURITY.md for security guidelines
- API documentation
- Setup and deployment guides
- User documentation for email templates and workflow
- API client documentation and setup procedures
- MCP-powered Actor integration documentation
- Frontend component documentation

## Task Management
- Track all tasks in TASK.md
- Mark completed tasks promptly
- Document discovered tasks under "Discovered During Work"
- Include deadlines for critical tasks 