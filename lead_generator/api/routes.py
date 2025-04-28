"""API routes for the Lead Generator.

This module defines all the API endpoints for the Lead Generator application.
"""

import logging
import os
from datetime import timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lead_generator.api import auth
from lead_generator.api.api_service import APIService
from lead_generator.api.middleware import add_middleware
from lead_generator.database.models import LeadStatus, init_db
from lead_generator.database.models import Base as DatabaseBase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lead_generator.db")
engine = init_db(DB_PATH)

# Database session dependency
def get_db():
    """Get database session."""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API service dependency
def get_api_service(db: Session = Depends(get_db)):
    """Get API service instance."""
    return APIService(db)

# Models
class LeadBase(BaseModel):
    """Base model for leads."""
    organization: str
    person_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    source_url: Optional[str] = None

class LeadCreate(LeadBase):
    """Model for creating leads."""
    pass

class Lead(LeadBase):
    """Model for leads with unique identifier."""
    id: int
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True

class LeadDetail(Lead):
    """Detailed lead model including email generations and status history."""
    email_generations: List[Dict[str, Any]] = []
    status_history: List[Dict[str, Any]] = []

class PaginationResult(BaseModel):
    """Model for paginated results."""
    items: List[Lead]
    total: int
    page: int
    pages: int
    per_page: int

class StatisticsResponse(BaseModel):
    """Model for statistics response."""
    date: str
    emails_sent: int
    emails_opened: int
    responses_received: int
    meetings_booked: int
    leads_by_status: Dict[str, int]
    recent_generations: List[Dict[str, Any]]
    available_templates: List[str]

class EmailGenRequest(BaseModel):
    """Model for email generation request."""
    lead_id: int
    template_name: str = "default"
    custom_variables: Optional[Dict[str, str]] = None

class EmailSendRequest(BaseModel):
    """Model for email send request."""
    generation_id: int

class StatusUpdateRequest(BaseModel):
    """Model for status update request."""
    lead_id: int
    status: str
    notes: Optional[str] = None

class ExportRequest(BaseModel):
    """Model for export request."""
    output_file: Optional[str] = None
    statuses: Optional[List[str]] = None

def create_app() -> FastAPI:
    """Create the FastAPI application."""
    # Determine if we're in debug mode
    debug_mode = os.getenv("API_DEBUG", "false").lower() == "true"
    
    app = FastAPI(
        title="Lead Generator API",
        description="API for managing leads from the Lead Generator application",
        version="1.0.0",
        debug=debug_mode
    )
    
    # Define allowed origins from environment variable or use defaults
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
        # Default allowed origins
        ALLOWED_ORIGINS = [
            "http://localhost:3000",     # Local development frontend
            "http://localhost:8080",     # Local development alternative
            "http://localhost:5173",     # Vite development server
            "http://localhost:5174",     # Vite fallback port
            "http://localhost:5175",     # Additional Vite port
            "https://lead-generator.example.com",  # Production frontend
        ]
        
    logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")
    
    # Setup CORS with secure configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,  # Restrict to specific origins only
        allow_credentials=True,         # Allow cookies to be sent with requests
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly enumerate allowed methods
        allow_headers=[
            "Authorization", 
            "Content-Type", 
            "Accept", 
            "Origin", 
            "X-Requested-With",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Credentials",
        ],  # Explicitly enumerate allowed headers
        expose_headers=[
            "Content-Length", 
            "Content-Type", 
            "X-Pagination-Total-Count", 
            "X-Pagination-Total-Pages"
        ],  # Headers that can be exposed to the browser
        max_age=600,  # Cache preflight requests for 10 minutes
    )
    
    # Add custom middleware for rate limiting and request logging
    add_middleware(app, rate_limit=60, debug=debug_mode)  # 60 requests per minute
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(leads_router)
    app.include_router(emails_router)
    app.include_router(dashboard_router)
    
    return app

# Authentication Router
auth_router = APIRouter(tags=["authentication"], prefix="/auth")

@auth_router.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get an access token.
    
    Args:
        form_data: Username and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"Generated access token for user {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me", response_model=auth.User)
async def read_users_me(current_user: auth.User = Depends(auth.get_current_active_user)):
    """Get information about the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user

# Leads Router
leads_router = APIRouter(tags=["leads"], prefix="/leads")

@leads_router.get("/", response_model=List[Lead])
async def get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    current_user: auth.User = Depends(auth.has_permission("read")),
    api_service: APIService = Depends(get_api_service)
):
    """Get leads with optional filters.
    
    Args:
        status: Filter by lead status
        source: Filter by lead source
        current_user: Current authenticated user with read permission
        api_service: API service instance
        
    Returns:
        List of leads
    """
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = LeadStatus[status.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid lead status: {status}"
                )
        
        # Get leads
        leads = api_service.get_all_leads(status_enum, source)
        
        logger.info(f"Retrieved {len(leads)} leads for user {current_user.username}")
        return leads
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving leads: {str(e)}"
        )

@leads_router.get("/{lead_id}", response_model=LeadDetail)
async def get_lead(
    lead_id: int,
    current_user: auth.User = Depends(auth.has_permission("read")),
    api_service: APIService = Depends(get_api_service)
):
    """Get a lead by ID.
    
    Args:
        lead_id: Lead ID
        current_user: Current authenticated user with read permission
        api_service: API service instance
        
    Returns:
        Lead details
    """
    try:
        lead = api_service.get_lead_by_id(lead_id)
        logger.info(f"Retrieved lead {lead_id} for user {current_user.username}")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving lead: {str(e)}"
        )

@leads_router.post("/status", response_model=LeadDetail)
async def update_lead_status(
    request: StatusUpdateRequest,
    current_user: auth.User = Depends(auth.has_permission("write")),
    api_service: APIService = Depends(get_api_service)
):
    """Update a lead's status.
    
    Args:
        request: Status update request
        current_user: Current authenticated user with write permission
        api_service: API service instance
        
    Returns:
        Updated lead details
    """
    try:
        # Convert status string to enum
        try:
            status_enum = LeadStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid lead status: {request.status}"
            )
        
        # Update lead status
        updated_lead = api_service.update_lead_status(
            request.lead_id, 
            status_enum, 
            request.notes
        )
        
        logger.info(f"Updated lead {request.lead_id} status to {request.status} by user {current_user.username}")
        return updated_lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating lead status: {str(e)}"
        )

@leads_router.post("/export", status_code=status.HTTP_202_ACCEPTED)
async def export_leads(
    request: ExportRequest,
    current_user: auth.User = Depends(auth.has_permission("export")),
    api_service: APIService = Depends(get_api_service)
):
    """Export leads to CSV.
    
    Args:
        request: Export request
        current_user: Current authenticated user with export permission
        api_service: API service instance
        
    Returns:
        Export result
    """
    try:
        # Convert status strings to enums if provided
        status_enums = None
        if request.statuses:
            status_enums = []
            for status_str in request.statuses:
                try:
                    status_enums.append(LeadStatus[status_str.upper()])
                except KeyError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid lead status: {status_str}"
                    )
        
        # Export leads
        result = api_service.export_leads_to_csv(request.output_file, status_enums)
        
        logger.info(f"Exported {result['lead_count']} leads to {result['file_path']} by user {current_user.username}")
        return {
            "message": f"Successfully exported {result['lead_count']} leads to {result['file_path']}",
            "file_path": result["file_path"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting leads: {str(e)}"
        )

# Emails Router
emails_router = APIRouter(tags=["emails"], prefix="/emails")

@emails_router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_email(
    request: EmailGenRequest,
    current_user: auth.User = Depends(auth.has_permission("email")),
    api_service: APIService = Depends(get_api_service)
):
    """Generate an email for a lead.
    
    Args:
        request: Email generation request
        current_user: Current authenticated user with email permission
        api_service: API service instance
        
    Returns:
        Generated email
    """
    try:
        result = api_service.generate_email(
            request.lead_id,
            request.template_name,
            request.custom_variables
        )
        
        logger.info(f"Generated email for lead {request.lead_id} by user {current_user.username}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating email: {str(e)}"
        )

@emails_router.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send_email(
    request: EmailSendRequest,
    background_tasks: BackgroundTasks,
    current_user: auth.User = Depends(auth.has_permission("email")),
    api_service: APIService = Depends(get_api_service)
):
    """Send a generated email.
    
    Args:
        request: Email send request
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user with email permission
        api_service: API service instance
        
    Returns:
        Success message
    """
    try:
        result = api_service.send_email(request.generation_id, background_tasks)
        
        logger.info(f"Email sending scheduled for generation {request.generation_id} by user {current_user.username}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )

# Dashboard Router
dashboard_router = APIRouter(tags=["dashboard"], prefix="/dashboard")

@dashboard_router.get("/stats", response_model=StatisticsResponse)
async def get_dashboard_stats(
    current_user: auth.User = Depends(auth.has_permission("read")),
    api_service: APIService = Depends(get_api_service)
):
    """Get dashboard statistics.
    
    Args:
        current_user: Current authenticated user with read permission
        api_service: API service instance
        
    Returns:
        Dashboard statistics
    """
    try:
        stats = api_service.get_dashboard_statistics()
        
        logger.info(f"Retrieved dashboard statistics for user {current_user.username}")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard statistics: {str(e)}"
        )

# Create the app
app = create_app() 