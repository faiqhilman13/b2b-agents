"""Main FastAPI application for the Malaysian Lead Generator API.

This module provides the API endpoints for accessing and managing leads.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lead_generator/logs/api.log")
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Malaysian Lead Generator API",
    description="API for accessing and managing leads from various Malaysian sources",
    version="0.1.0"
)

# Add CORS middleware
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

# Security configuration
SECRET_KEY = os.getenv("API_SECRET_KEY", None)
if not SECRET_KEY:
    # Generate a random secure key if not provided
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "API_SECRET_KEY environment variable not set. Using a generated key. "
        "This key will change on restart, invalidating all tokens!"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Define models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class Lead(BaseModel):
    id: Optional[str] = None
    name: str
    organization: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str
    scrape_date: Optional[str] = None
    notes: Optional[str] = None

# Fake user database for demo - replace with real database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "fakehashedsecret",  # In production, use proper hashing
        "disabled": False,
    }
}

# OAuth2 authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password verification
    return plain_password == "secret" and hashed_password == "fakehashedsecret"

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def load_leads_from_file(filename: str) -> List[Dict[str, Any]]:
    """Load leads from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading leads from {filename}: {e}")
        return []

# Define API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/leads", response_model=List[Lead])
async def get_leads(
    current_user: User = Depends(get_current_active_user),
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get leads from the database."""
    # For demonstration, we'll load leads from a JSON file
    # In production, this would come from a database
    all_leads = []
    
    # Load from business list
    business_leads = load_leads_from_file("lead_generator/data/business_list_leads.json")
    for lead in business_leads:
        lead["source"] = "business_list"
    all_leads.extend(business_leads)
    
    # Load from government ministries
    gov_leads = load_leads_from_file("lead_generator/data/government_leads.json")
    for lead in gov_leads:
        lead["source"] = "government"
    all_leads.extend(gov_leads)
    
    # Load from universities
    uni_leads = load_leads_from_file("lead_generator/data/university_leads.json")
    for lead in uni_leads:
        lead["source"] = "university"
    all_leads.extend(uni_leads)
    
    # Filter by source if provided
    if source:
        all_leads = [lead for lead in all_leads if lead["source"] == source]
    
    # Apply pagination
    paginated_leads = all_leads[offset:offset + limit]
    
    return paginated_leads

@app.get("/leads/count")
async def get_leads_count(
    current_user: User = Depends(get_current_active_user),
    source: Optional[str] = None
):
    """Get the count of leads by source."""
    # For demonstration, we'll load leads from JSON files
    # In production, this would come from a database
    business_count = len(load_leads_from_file("lead_generator/data/business_list_leads.json"))
    gov_count = len(load_leads_from_file("lead_generator/data/government_leads.json"))
    uni_count = len(load_leads_from_file("lead_generator/data/university_leads.json"))
    
    counts = {
        "business_list": business_count,
        "government": gov_count,
        "university": uni_count,
        "total": business_count + gov_count + uni_count
    }
    
    if source:
        return {"count": counts.get(source, 0)}
    
    return counts

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"message": "Malaysian Lead Generator API is running", "version": "0.1.0"} 