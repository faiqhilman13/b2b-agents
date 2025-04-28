# System Patterns: B2B Lead Generator

## Architectural Patterns

### Overall Architecture
- **Microservices-Based Approach**: The system is structured around discrete, specialized services for lead discovery, verification, enrichment, and data management
- **Event-Driven Architecture**: Services communicate via events for asynchronous processing of long-running tasks
- **API Gateway Pattern**: A central gateway manages authentication, routing, and rate limiting for all external requests
- **Worker Pool Pattern**: Distributed workers process scraping and verification tasks from queues

### Data Flow Architecture
```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Data Sources │ → │ Lead Discovery │ → │ Verification & │ → │  Data Storage  │
│  & Ingestion  │    │   Service     │    │  Enrichment   │    │  & Retrieval  │
└───────────────┘    └───────────────┘    └───────────────┘    └───────────────┘
        ↑                                                              ↓
        │                                                              │
        │              ┌───────────────┐    ┌───────────────┐         │
        └─────────────┤     User       │←───┤  Reporting &  │←────────┘
                      │   Interface    │    │   Analytics   │
                      └───────────────┘    └───────────────┘
```

## Code Organization

### Project Structure
```
b2b_lead_generator/
├── api/                  # API endpoints and gateway
│   ├── routes/           # API route definitions
│   ├── middleware/       # Request/response middleware
│   └── schemas/          # Request/response data models
├── core/                 # Core application logic
│   ├── config/           # Configuration management
│   ├── discovery/        # Lead discovery services
│   ├── verification/     # Email & contact verification
│   ├── enrichment/       # Data enrichment services
│   └── analytics/        # Data analysis and reporting
├── data/                 # Data management
│   ├── models/           # Database models
│   ├── repositories/     # Data access layer
│   └── migrations/       # Database migration scripts
├── services/             # External service integrations
│   ├── email/            # Email verification services
│   ├── scraping/         # Web scraping utilities
│   └── third_party/      # Third-party API integrations
├── workers/              # Background task workers
│   ├── scrapers/         # Web scraping workers
│   ├── verifiers/        # Email verification workers
│   └── enrichers/        # Data enrichment workers
├── ui/                   # User interface components
│   ├── dashboard/        # Dashboard views
│   ├── lead_management/  # Lead management interface
│   └── reports/          # Reporting and analytics UI
├── utils/                # Utility functions and helpers
│   ├── validators/       # Input validation utilities
│   ├── formatting/       # Data formatting utilities
│   └── logging/          # Logging configuration
└── tests/                # Test suites
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── e2e/              # End-to-end tests
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `api` | Handles HTTP requests and responses, routing, and API documentation |
| `core` | Implements core business logic for lead generation and processing |
| `data` | Manages data persistence, retrieval, and database interactions |
| `services` | Provides integrations with external services and APIs |
| `workers` | Executes background and long-running tasks |
| `ui` | Implements user interface components and views |
| `utils` | Contains shared utilities and helper functions |
| `tests` | Provides comprehensive test coverage |

## Design Patterns

### Core Patterns
- **Repository Pattern**: Abstracts data access logic from business logic
- **Factory Pattern**: Creates complex objects for scrapers and verification strategies
- **Strategy Pattern**: Allows interchangeable verification and enrichment algorithms
- **Observer Pattern**: Enables reactive updates when lead data changes
- **Command Pattern**: Encapsulates scraping and verification requests as objects

### Service Patterns
- **Circuit Breaker**: Prevents cascading failures when external services are unavailable
- **Retry Pattern**: Automatically retries failed operations with backoff
- **Throttling Pattern**: Limits rate of requests to external services
- **Bulkhead Pattern**: Isolates failures to prevent system-wide issues

## Coding Standards

### General Standards
- Follow PEP 8 style guide for Python code
- Use type hints consistently throughout the codebase
- Document all public functions, classes, and modules with docstrings
- Keep functions focused on a single responsibility
- Limit function length to maximum 50 lines

### Naming Conventions
- **Classes**: CamelCase (e.g., `LeadVerifier`, `EmailValidator`)
- **Functions/Methods**: snake_case (e.g., `verify_email`, `extract_contact_info`)
- **Variables**: snake_case (e.g., `lead_count`, `verification_status`)
- **Constants**: UPPER_CASE (e.g., `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`)
- **Private members**: Prefix with underscore (e.g., `_internal_state`, `_validate_input`)

### Documentation Standards
- Use Google-style docstrings for all public APIs
- Document parameters, return values, and exceptions
- Include usage examples for complex functions
- Maintain up-to-date API documentation using FastAPI's built-in tools

```python
def verify_email(email: str, timeout: int = 10) -> VerificationResult:
    """
    Verifies if an email address is valid and deliverable.
    
    Args:
        email: Email address to verify
        timeout: Timeout in seconds for SMTP verification
        
    Returns:
        VerificationResult object containing status and confidence score
        
    Raises:
        InvalidEmailError: If email format is invalid
        TimeoutError: If verification exceeds timeout
        
    Example:
        >>> result = verify_email("test@example.com")
        >>> if result.is_valid:
        ...     print(f"Valid email with {result.confidence}% confidence")
    """
    # Implementation
```

## Testing Strategies

### Test Types
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete workflows from user perspective
- **Performance Tests**: Verify system meets performance requirements

### Test Guidelines
- Maintain minimum 80% code coverage for all modules
- Mock external dependencies in unit tests
- Use fixture-based setup for test data
- Implement automated CI/CD pipeline with test gates
- Include both positive and negative test cases

## Error Handling

### Error Handling Patterns
- Use custom exception classes for different error types
- Implement centralized error logging and monitoring
- Return appropriate HTTP status codes for API errors
- Provide helpful error messages for troubleshooting

### Error Recovery
- Implement automatic retries for transient failures
- Use dead-letter queues for unprocessable messages
- Track and alert on error rates and patterns
- Provide self-healing mechanisms where possible

## Logging and Monitoring

### Logging Standards
- Use structured logging (JSON format)
- Include context information in all log entries
- Define and use appropriate log levels consistently
- Implement request ID tracking across services

### Monitoring Strategy
- Track key performance indicators (KPIs) for all services
- Implement health checks for all components
- Set up alerts for abnormal conditions
- Monitor resource utilization and performance metrics

## Security Practices

### Development Security
- Conduct regular code reviews with security focus
- Use static code analysis tools to identify vulnerabilities
- Follow secure coding practices (input validation, output encoding)
- Avoid hardcoded secrets and credentials

### Runtime Security
- Implement proper authentication and authorization
- Encrypt sensitive data at rest and in transit
- Apply rate limiting to prevent abuse
- Regularly update dependencies to patch vulnerabilities

## Deployment Strategy

### CI/CD Pipeline
- Automate builds, tests, and deployments
- Implement branch-based workflows (e.g., GitFlow)
- Use infrastructure as code for environment management
- Perform automated security scanning during CI process

### Environment Management
- Maintain separate development, staging, and production environments
- Use configuration management for environment-specific settings
- Implement feature toggles for controlled rollouts
- Support zero-downtime deployments

## Collaboration Guidelines

### Version Control Practices
- Use feature branches for all changes
- Require pull requests for code review
- Write meaningful commit messages
- Follow semantic versioning for releases

### Code Review Standards
- Review all code changes before merging
- Focus on security, performance, and maintainability
- Use automated tools to enforce style and quality standards
- Document architecture decisions and rationales 