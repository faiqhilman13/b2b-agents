"""
Base client for MCP-powered Apify Actor integration.

This module provides a base class for API clients that connect to
MCP-powered Apify Actors. It handles authentication, rate limiting,
caching, and error handling common to all API clients.
"""

import time
import logging
import json
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Custom exception classes for API clients
class ApiClientError(Exception):
    """Base exception for all API client errors."""
    pass

class ApiConnectionError(ApiClientError):
    """Exception raised when connection to the API fails."""
    pass

class ApiTimeoutError(ApiClientError):
    """Exception raised when an API request times out."""
    pass

class ApiResponseError(ApiClientError):
    """Exception raised when the API returns an error response."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

class ApiAuthenticationError(ApiClientError):
    """Exception raised when API authentication fails."""
    pass

class ApiRateLimitError(ApiClientError):
    """Exception raised when API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(message)

class ApiConfigurationError(ApiClientError):
    """Exception raised when API client is misconfigured."""
    pass

class BaseApiClient:
    """Base class for MCP-powered Apify Actor clients."""
    
    def __init__(self, cache_dir: str = "cache", cache_ttl: int = 86400):
        """
        Initialize the base API client.
        
        Args:
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # Seconds between requests
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"Initialized {self.__class__.__name__} with cache in {cache_dir}")
    
    def _get_cache_path(self, cache_key: str) -> str:
        """
        Get the path to a cache file.
        
        Args:
            cache_key: Unique identifier for the cache entry
            
        Returns:
            Path to the cache file
        """
        # Create a safe filename from the cache key
        safe_key = "".join(c if c.isalnum() else "_" for c in cache_key)
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from the cache if it exists and is not expired.
        
        Args:
            cache_key: Unique identifier for the cache entry
            
        Returns:
            Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            if not os.path.exists(cache_path):
                return None
                
            # Check if the cache file is expired
            file_modified_time = os.path.getmtime(cache_path)
            if time.time() - file_modified_time > self.cache_ttl:
                logger.debug(f"Cache expired for {cache_key}")
                return None
                
            # Read the cache file
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Retrieved data from cache for {cache_key}")
                return data
                
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """
        Save data to the cache.
        
        Args:
            cache_key: Unique identifier for the cache entry
            data: Data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.debug(f"Saved data to cache for {cache_key}")
                return True
        except Exception as e:
            logger.warning(f"Error saving to cache: {e}")
            return False
    
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to avoid overloading the API."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _standardize_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Standardize API response data to a common format.
        
        This method should be implemented by subclasses to transform
        API-specific response formats into a standard lead format.
        
        Args:
            raw_data: Raw data from the API
            
        Returns:
            Standardized list of lead data dictionaries
        """
        raise NotImplementedError("Subclasses must implement _standardize_data")
    
    def execute_query(self, 
                     query: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the API.
        
        Args:
            query: The search query or identifier
            params: Additional parameters for the query
            use_cache: Whether to use cached results if available
            
        Returns:
            API response data
        """
        # This is a placeholder - subclasses should implement the actual API call
        raise NotImplementedError("Subclasses must implement execute_query") 