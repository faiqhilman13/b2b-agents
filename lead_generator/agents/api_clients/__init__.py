"""
API client modules for MCP-powered Apify Actor integration.

This package provides client adapters for various data sources:
- Google Maps (gmaps-proxy)
- Instagram Scraper
- RAG Web Browser

These clients facilitate the acquisition of business contact information
from reliable external sources.
"""

import os
import logging
from typing import Dict, Any, Optional

# Import implemented clients
from .gmaps_client import GoogleMapsClient
from .web_browser_client import WebBrowserClient
from .instagram_client import InstagramClient  # Now fully implemented

# Import exceptions
from .base_client import (
    ApiClientError, 
    ApiConnectionError,
    ApiTimeoutError,
    ApiResponseError,
    ApiAuthenticationError,
    ApiRateLimitError,
    ApiConfigurationError
)

# Set up logging
logger = logging.getLogger(__name__)

__all__ = [
    'GoogleMapsClient',
    'WebBrowserClient',
    'InstagramClient',
    'activate_clients',
    'get_client',
    
    'ApiClientError',
    'ApiConnectionError',
    'ApiTimeoutError',
    'ApiResponseError',
    'ApiAuthenticationError',
    'ApiRateLimitError',
    'ApiConfigurationError'
]

# Dictionary to store active client instances
_active_clients: Dict[str, Any] = {}

def activate_clients(api_endpoints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Activate and initialize API clients with their endpoints.
    
    Args:
        api_endpoints: Dictionary mapping client names to their API endpoints.
                       If None, will try to get from environment variables.
    
    Returns:
        Dictionary of initialized client instances.
    """
    global _active_clients
    
    # If no endpoints provided, try to get from environment variables
    if api_endpoints is None:
        api_endpoints = {
            'google_maps': os.getenv('GMAPS_API_ENDPOINT'),
            'web_browser': os.getenv('WEB_BROWSER_API_ENDPOINT'),
            'instagram': os.getenv('INSTAGRAM_API_ENDPOINT')
        }
    
    # Initialize Google Maps client if endpoint available
    if api_endpoints.get('google_maps'):
        _active_clients['google_maps'] = GoogleMapsClient(
            api_endpoint=api_endpoints['google_maps']
        )
        logger.info("Google Maps client activated")
    
    # Initialize Web Browser client if endpoint available
    if api_endpoints.get('web_browser'):
        _active_clients['web_browser'] = WebBrowserClient(
            api_endpoint=api_endpoints['web_browser']
        )
        logger.info("Web Browser client activated")
    
    # Initialize Instagram client if endpoint available and client implemented
    if api_endpoints.get('instagram'):
        _active_clients['instagram'] = InstagramClient(
            api_endpoint=api_endpoints['instagram']
        )
        logger.info("Instagram client activated")
    
    return _active_clients

def get_client(client_name: str) -> Optional[Any]:
    """
    Get an initialized API client by name.
    
    Args:
        client_name: Name of the client to get ('google_maps', 'web_browser', 'instagram')
    
    Returns:
        Initialized client instance or None if not found
    """
    if not _active_clients and os.getenv('AUTO_ACTIVATE_CLIENTS', 'true').lower() == 'true':
        # Auto-activate clients if not yet activated
        activate_clients()
    
    return _active_clients.get(client_name) 