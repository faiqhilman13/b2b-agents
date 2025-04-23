"""API Data Models for Lead Generator.

This module defines the Pydantic models used for data validation and serialization
in the Lead Generator API. These models ensure that all incoming data is properly
validated and that all outgoing data is correctly formatted.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator, root_validator
import re


class LeadStatusEnum(str, Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDING = "responding"
    QUALIFIED = "qualified"
    MEETING_BOOKED = "meeting_booked"
    DEAL_CLOSED = "deal_closed"
    NO_RESPONSE = "no_response"
    NOT_INTERESTED = "not_interested"
    INVALID = "invalid"


class LeadBase(BaseModel):
    """Base model for lead data with all required validations."""
    organization: str = Field(..., min_length=2, max_length=200)
    person_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    role: Optional[str] = Field(None, max_length=100)
    source_url: Optional[HttpUrl] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        # Basic length check
        if len(digits_only) < 6 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 6 and 15 digits")
            
        return v
    
    @validator('person_name')
    def validate_person_name(cls, v):
        """Validate person name contains no suspicious content."""
        if v is None:
            return v
            
        # Check for potential script injection
        if '<' in v or '>' in v or '{' in v or '}' in v:
            raise ValueError("Name contains invalid characters")
            
        return v


class LeadCreate(LeadBase):
    """Model for creating a new lead."""
    # We can add additional fields or validations specific to creation here
    pass


class Lead(LeadBase):
    """Model for lead data including database fields."""
    id: int
    status: LeadStatusEnum
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True


class LeadUpdate(BaseModel):
    """Model for updating lead data, all fields optional."""
    organization: Optional[str] = Field(None, min_length=2, max_length=200)
    person_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    role: Optional[str] = Field(None, max_length=100)
    source_url: Optional[HttpUrl] = None
    status: Optional[LeadStatusEnum] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        # Basic length check
        if len(digits_only) < 6 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 6 and 15 digits")
            
        return v
    
    @root_validator
    def check_at_least_one_field(cls, values):
        """Ensure at least one field is being updated."""
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values


class EmailGenerationBase(BaseModel):
    """Base model for email generation data."""
    lead_id: int
    template_name: str = Field(..., min_length=1, max_length=50)
    custom_variables: Optional[Dict[str, str]] = None
    
    @validator('template_name')
    def validate_template_name(cls, v):
        """Validate template name to prevent path traversal."""
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Template name contains invalid characters")
        return v
    
    @validator('custom_variables')
    def validate_custom_variables(cls, v):
        """Validate custom variables don't contain suspicious content."""
        if v is None:
            return v
            
        for key, value in v.items():
            if '<script' in str(value).lower():
                raise ValueError(f"Variable '{key}' contains potentially unsafe content")
                
        return v


class EmailGeneration(EmailGenerationBase):
    """Model for email generation data including database fields."""
    id: int
    subject: str
    body: str
    to_email: EmailStr
    generated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True


class EmailSendRequest(BaseModel):
    """Model for email send request."""
    generation_id: int


class EmailSendWithAttachmentRequest(EmailSendRequest):
    """Model for email send request with attachment."""
    proposal_path: str
    
    @validator('proposal_path')
    def validate_proposal_path(cls, v):
        """Validate proposal path to prevent path traversal."""
        if '..' in v:
            raise ValueError("Proposal path contains invalid traversal")
            
        if not v.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported for proposals")
            
        return v


class LeadDetail(Lead):
    """Detailed lead model including email generations and status history."""
    email_generations: List[EmailGeneration] = []
    status_history: List[Dict[str, Any]] = []


class PaginationParams(BaseModel):
    """Model for pagination parameters."""
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=5, le=100)


class PaginatedResponse(BaseModel):
    """Generic model for paginated responses."""
    items: List[Any]
    total: int
    page: int
    pages: int
    per_page: int


class StatusUpdateRequest(BaseModel):
    """Model for status update request."""
    lead_id: int
    status: LeadStatusEnum
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('notes')
    def validate_notes(cls, v):
        """Validate notes don't contain malicious content."""
        if v is None:
            return v
            
        if '<script' in v.lower() or 'javascript:' in v.lower():
            raise ValueError("Notes contain potentially unsafe content")
            
        return v


class ExportRequest(BaseModel):
    """Model for export request."""
    output_file: Optional[str] = Field(None, max_length=255)
    statuses: Optional[List[LeadStatusEnum]] = None
    
    @validator('output_file')
    def validate_output_file(cls, v):
        """Validate output file to prevent path traversal."""
        if v is None:
            return v
            
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Output file contains invalid characters")
            
        return v


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ApiErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None 