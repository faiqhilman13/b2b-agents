"""Authentication module for the Lead Generator API.

This module provides functions for user authentication, token generation and validation.
"""

import os
import json
import logging
import secrets
import time
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               "config", "users.json")

# Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    permissions: List[str] = []

class UserInDB(User):
    hashed_password: str

# Simple in-memory user store (replace with database in production)
USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),  # Default password for development
        "full_name": "Administrator",
        "email": "admin@leadgenerator.com",
        "is_active": True,
        "is_admin": True
    }
}

def load_users(users_file: str = DEFAULT_USERS_FILE) -> Dict[str, UserInDB]:
    """Load users from a JSON file.
    
    Args:
        users_file: Path to the users JSON file
        
    Returns:
        Dictionary mapping usernames to UserInDB objects
    """
    try:
        if not os.path.exists(users_file):
            logger.warning(f"Users file not found at {users_file}, creating default admin user")
            # Create a default admin user if file doesn't exist
            default_user = {
                "admin": {
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "Administrator",
                    "disabled": False,
                    "hashed_password": get_password_hash("admin"),
                    "permissions": ["admin", "read", "write", "email"]
                }
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(users_file)), exist_ok=True)
            
            # Write default user to file
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_user, f, indent=4)
            
            return default_user
            
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            
            # Convert dictionary to UserInDB objects
            users = {}
            for username, user_data in users_data.items():
                users[username] = UserInDB(**user_data)
                
            logger.info(f"Loaded {len(users)} users from {users_file}")
            return users
    except Exception as e:
        logger.error(f"Error loading users from {users_file}: {str(e)}")
        # Return default admin user in case of error
        return {
            "admin": UserInDB(
                username="admin",
                email="admin@example.com",
                full_name="Administrator",
                disabled=False,
                hashed_password=get_password_hash("admin"),
                permissions=["admin", "read", "write", "email"]
            )
        }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[Dict]:
    """Get user by username.

    Args:
        username: Username to look up

    Returns:
        User data dictionary or None if not found
    """
    return USERS.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        User data dictionary or None if authentication fails
    """
    user = get_user(username)
    if not user:
        logger.warning(f"Authentication failed: User {username} not found")
        return None
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Authentication failed: Invalid password for user {username}")
        return None
    if not user.get("is_active", False):
        logger.warning(f"Authentication failed: User {username} is inactive")
        return None
    
    logger.info(f"User {username} authenticated successfully")
    return user

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(data.get("username", ""))
    })
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created token for user {data.get('username')}")
    
    return token

def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if username is None:
            logger.warning("Token validation failed: missing subject")
            return None
            
        # Get the user data
        user = get_user(username)
        if user is None:
            logger.warning(f"Token validation failed: user {username} not found")
            return None
            
        if not user.get("is_active", False):
            logger.warning(f"Token validation failed: user {username} is inactive")
            return None
            
        logger.info(f"Token validated for user {username}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed: token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        return None

def get_current_user_from_token(token: str) -> Optional[Dict]:
    """Get current user from token.

    Args:
        token: JWT token

    Returns:
        User data dictionary or None if token is invalid
    """
    payload = verify_token(token)
    if payload is None:
        return None
        
    username = payload.get("sub")
    return get_user(username)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a token.
    
    Args:
        token: JWT access token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
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
        logger.error("Invalid JWT token")
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        logger.error(f"User {token_data.username} not found")
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if active
        
    Raises:
        HTTPException: If the user is disabled
    """
    if current_user.disabled:
        logger.warning(f"Disabled user {current_user.username} attempted to access the API")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_permission(required_permission: str):
    """Check if user has a required permission.
    
    Args:
        required_permission: The permission to check for
        
    Returns:
        A dependency function that checks for the required permission
    """
    async def check_permission(current_user: User = Depends(get_current_active_user)) -> User:
        if "admin" in current_user.permissions or required_permission in current_user.permissions:
            return current_user
        logger.warning(f"User {current_user.username} does not have permission: {required_permission}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to perform this action. Required: {required_permission}"
        )
    return check_permission 