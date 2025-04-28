"""
Google Maps client for MCP-powered Apify Actor integration.

This module provides a client to interact with the gmaps-proxy
MCP-powered Apify Actor, which extracts business information
from Google Maps.
"""

import logging
import json
import hashlib
from typing import Dict, Any, List, Optional, Union
import requests

from .base_client import BaseApiClient

# Set up logging
logger = logging.getLogger(__name__)

class GoogleMapsClient(BaseApiClient):
    """Client for interacting with the Google Maps MCP-powered Actor."""
    
    def __init__(self, 
                api_endpoint: str = None,
                cache_dir: str = "cache/google_maps", 
                cache_ttl: int = 86400):
        """
        Initialize the Google Maps client.
        
        Args:
            api_endpoint: The MCP-powered API endpoint (from Cursor)
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(cache_dir, cache_ttl)
        self.api_endpoint = api_endpoint
        logger.info("Initialized Google Maps client")
        
    def search_businesses(self, 
                         query: str, 
                         location: Optional[str] = None,
                         limit: int = 20,
                         use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for businesses on Google Maps.
        
        Args:
            query: Search query (e.g., "accounting firms")
            location: Optional location to focus search (e.g., "Kuala Lumpur")
            limit: Maximum number of results to return
            use_cache: Whether to use cached results if available
            
        Returns:
            List of standardized business data
        """
        # Combine query and location if provided
        full_query = query
        if location:
            full_query = f"{query} in {location}"
            
        # Generate a cache key
        cache_key = f"gmaps_{hashlib.md5(full_query.encode()).hexdigest()}_{limit}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved {len(cached_data['results'])} Google Maps results from cache for '{full_query}'")
                return self._standardize_data(cached_data)
        
        # Execute the query
        raw_data = self.execute_query(full_query, {"limit": limit}, use_cache=False)
        
        # Save to cache if results were found
        if raw_data and "results" in raw_data:
            self._save_to_cache(cache_key, raw_data)
            
        # Standardize and return the data
        return self._standardize_data(raw_data)
    
    def execute_query(self, 
                     query: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the Google Maps API.
        
        Args:
            query: The search query
            params: Additional parameters for the query
            use_cache: Whether to use cached results (handled by search_businesses)
            
        Returns:
            API response data
        """
        # Apply rate limiting
        self._apply_rate_limiting()
        
        if not self.api_endpoint:
            logger.error("API endpoint not configured for Google Maps client")
            return {"error": "API endpoint not configured", "results": []}
        
        try:
            # Prepare the request payload
            payload = {
                "url": query,
                **(params or {})
            }
            
            # Here we would make the actual API call to the MCP-powered Actor
            # For now, return a placeholder response
            logger.info(f"Executing Google Maps query: '{query}'")
            
            # Placeholder - Replace with actual MCP API call
            # return requests.post(self.api_endpoint, json=payload).json()
            
            # Placeholder response
            return {
                "status": "success",
                "results": [
                    {
                        "name": "Example Business 1",
                        "address": "123 Main St, Kuala Lumpur, Malaysia",
                        "phone": "+60123456789",
                        "website": "https://example.com",
                        "rating": 4.5,
                        "reviews": 120,
                        "category": "Accounting",
                        "coordinates": {
                            "latitude": 3.1390,
                            "longitude": 101.6869
                        }
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error executing Google Maps query: {e}")
            return {"error": str(e), "results": []}
    
    def _standardize_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Standardize Google Maps data to the common lead format.
        
        Args:
            raw_data: Raw data from the Google Maps API
            
        Returns:
            Standardized list of lead data dictionaries
        """
        if not raw_data or "error" in raw_data or "results" not in raw_data:
            logger.warning("No valid data to standardize from Google Maps")
            return []
            
        standardized_leads = []
        
        for business in raw_data["results"]:
            try:
                lead = {
                    "organization": business.get("name", ""),
                    "person_name": "",  # Google Maps typically doesn't have person names
                    "role": "",         # Google Maps typically doesn't have roles
                    "email": "",        # Google Maps typically doesn't have email addresses
                    "phone": business.get("phone", ""),
                    "address": business.get("address", ""),
                    "website": business.get("website", ""),
                    "source_url": f"https://www.google.com/maps/search/{business.get('name', '').replace(' ', '+')}",
                    "source_type": "google_maps",
                    "rating": business.get("rating", None),
                    "reviews_count": business.get("reviews", 0),
                    "categories": business.get("category", "").split(","),
                    "location": {
                        "latitude": business.get("coordinates", {}).get("latitude", None),
                        "longitude": business.get("coordinates", {}).get("longitude", None)
                    },
                    "metadata": {
                        "place_id": business.get("place_id", ""),
                        "raw_data": business
                    }
                }
                standardized_leads.append(lead)
            except Exception as e:
                logger.error(f"Error standardizing business data: {e}")
                continue
                
        logger.info(f"Standardized {len(standardized_leads)} leads from Google Maps data")
        return standardized_leads 