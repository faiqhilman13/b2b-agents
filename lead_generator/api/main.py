"""Main API module for Lead Generator.

This module provides the FastAPI application with routes for lead management,
authentication, and email operations.
"""

import os
import logging
from datetime import timedelta
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from lead_generator.api.auth import (
    Token, User, authenticate_user, create_access_token, 
    get_current_active_user, get_current_admin_user, 
    fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
)
from lead_generator.api.leads import (
    load_leads_from_file, get_all_leads, filter_leads, 
    paginate_leads, get_lead_statistics, export_leads_to_csv
)
from lead_generator.agents.email_sender import EmailSender

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Malaysian Lead Generator API",
    description="API for managing and interacting with the Malaysian Lead Generator",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development frontend
        "http://localhost:8080",  # Local development alternative
        "https://lead-generator.example.com",  # Production frontend
    ],  # Specific origins instead of wildcard "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods instead of "*"
    allow_headers=["Authorization", "Content-Type"],  # Specific headers instead of "*"
)

# Initialize email sender
email_sender = EmailSender()

# Define API routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route to obtain an access token.
    
    Args:
        form_data: Form containing username and password
        
    Returns:
        Token object with access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User {form_data.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
    """
    return current_user

# Lead management routes
@app.get("/leads", response_model=Dict)
async def get_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    organization: Optional[str] = None,
    has_email: Optional[bool] = None,
    has_phone: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get leads with optional filtering and pagination.
    
    Args:
        page: Page number
        per_page: Number of items per page
        source: Filter by lead source
        organization: Filter leads containing organization name
        has_email: Filter leads with/without email
        has_phone: Filter leads with/without phone
        current_user: Current authenticated user
        
    Returns:
        Dictionary with paginated leads and metadata
    """
    try:
        # Get and filter leads
        all_leads = get_all_leads()
        filtered_leads = filter_leads(
            all_leads, 
            source=source,
            organization=organization,
            has_email=has_email,
            has_phone=has_phone
        )
        
        # Paginate leads
        paginated_result = paginate_leads(filtered_leads, page, per_page)
        
        logger.info(f"User {current_user.username} retrieved {len(paginated_result['items'])} leads")
        return paginated_result
    except Exception as e:
        logger.error(f"Error retrieving leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving leads: {str(e)}"
        )

@app.get("/leads/statistics")
async def get_statistics(current_user: User = Depends(get_current_active_user)):
    """Get lead statistics.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary with lead statistics
    """
    try:
        all_leads = get_all_leads()
        stats = get_lead_statistics(all_leads)
        logger.info(f"User {current_user.username} retrieved lead statistics")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving lead statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving lead statistics: {str(e)}"
        )

@app.post("/leads/export")
async def export_leads(
    file_path: str,
    source: Optional[str] = None,
    organization: Optional[str] = None,
    has_email: Optional[bool] = None,
    has_phone: Optional[bool] = None,
    current_user: User = Depends(get_current_admin_user)  # Only admins can export
):
    """Export leads to CSV file.
    
    Args:
        file_path: Path to export CSV file
        source: Filter by lead source
        organization: Filter leads containing organization name
        has_email: Filter leads with/without email
        has_phone: Filter leads with/without phone
        current_user: Current authenticated admin user
        
    Returns:
        Success message
    """
    try:
        # Get and filter leads
        all_leads = get_all_leads()
        filtered_leads = filter_leads(
            all_leads, 
            source=source,
            organization=organization,
            has_email=has_email,
            has_phone=has_phone
        )
        
        # Export leads
        export_leads_to_csv(filtered_leads, file_path)
        
        logger.info(f"User {current_user.username} exported {len(filtered_leads)} leads to {file_path}")
        return {"message": f"Successfully exported {len(filtered_leads)} leads to {file_path}"}
    except Exception as e:
        logger.error(f"Error exporting leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting leads: {str(e)}"
        )

# Email operations routes
@app.post("/email/send")
async def send_email(
    background_tasks: BackgroundTasks,
    recipient: str,
    subject: str,
    body: str,
    current_user: User = Depends(get_current_admin_user)  # Only admins can send emails
):
    """Send an email.
    
    Args:
        background_tasks: FastAPI background tasks
        recipient: Email recipient
        subject: Email subject
        body: Email body
        current_user: Current authenticated admin user
        
    Returns:
        Success message
    """
    try:
        # Use background task to send email
        background_tasks.add_task(
            email_sender.send_email, 
            recipient=recipient,
            subject=subject,
            body=body
        )
        
        logger.info(f"User {current_user.username} initiated email send to {recipient}")
        return {"message": f"Email to {recipient} scheduled for sending"}
    except Exception as e:
        logger.error(f"Error scheduling email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling email: {str(e)}"
        )

@app.post("/email/batch-send")
async def send_batch_emails(
    background_tasks: BackgroundTasks,
    recipients: List[str],
    subject: str,
    body: str,
    current_user: User = Depends(get_current_admin_user)  # Only admins can send emails
):
    """Send batch emails.
    
    Args:
        background_tasks: FastAPI background tasks
        recipients: List of email recipients
        subject: Email subject
        body: Email body
        current_user: Current authenticated admin user
        
    Returns:
        Success message
    """
    try:
        # Use background task to send batch emails
        background_tasks.add_task(
            email_sender.send_batch_emails, 
            recipients=recipients,
            subject=subject,
            body=body
        )
        
        logger.info(f"User {current_user.username} initiated batch email send to {len(recipients)} recipients")
        return {"message": f"Batch email to {len(recipients)} recipients scheduled for sending"}
    except Exception as e:
        logger.error(f"Error scheduling batch email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling batch email: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    # Run the API server
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port) 