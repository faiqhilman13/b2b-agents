"""
Google Maps client for MCP-powered Apify Actor integration.

This module provides a client to interact with the Google Maps Proxy 
MCP-powered Apify Actor, which extracts business information from 
Google Maps listings.
"""

import logging
import json
import hashlib
import re
from typing import Dict, Any, List, Optional, Union
import requests
import urllib.parse
import os

from .base_client import BaseApiClient

# Set up logging
logger = logging.getLogger(__name__)

class GoogleMapsClient(BaseApiClient):
    """Client for interacting with the Google Maps Proxy MCP-powered Actor."""
    
    def __init__(self, 
                api_endpoint: str = None,
                cache_dir: str = "cache/gmaps", 
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
        self.rate_limit_delay = 5.0  # Delay between requests to avoid rate limiting
        logger.info("Initialized Google Maps client")
        
    def search_businesses(self, 
                         query: str, 
                         location: Optional[str] = None,
                         limit: int = 10,
                         use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for businesses on Google Maps.
        
        Args:
            query: Search query (e.g., "coffee shops")
            location: Optional location to focus search (e.g., "Kuala Lumpur")
            limit: Maximum number of results to return
            use_cache: Whether to use cached results if available
            
        Returns:
            List of standardized business data
        """
        # Construct the full search query
        full_query = query
        if location:
            full_query = f"{query} in {location}"
            
        # Generate a cache key
        cache_key = f"search_{hashlib.md5(full_query.encode()).hexdigest()}_{limit}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved Google Maps search results from cache for '{full_query}'")
                return cached_data
        
        # Construct the Google Maps search URL
        encoded_query = urllib.parse.quote_plus(full_query)
        url = f"https://www.google.com/maps/search/{encoded_query}"
        
        # Execute the query
        params = {
            "url": url
        }
        
        raw_data = self.execute_query(url, params, use_cache=False)
        
        # Process and standardize the results
        businesses = self._extract_businesses(raw_data, limit)
        
        # Save to cache if results were found
        if businesses:
            self._save_to_cache(cache_key, businesses)
            
        return businesses
    
    def get_business_details(self, 
                           place_id: str, 
                           use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific business.
        
        Args:
            place_id: Google Maps place ID
            use_cache: Whether to use cached results if available
            
        Returns:
            Standardized business data or None if not found
        """
        # Generate a cache key
        cache_key = f"business_{place_id}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved Google Maps business details from cache for place ID '{place_id}'")
                return cached_data
        
        # Construct the Google Maps place URL
        url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        
        # Execute the query
        params = {
            "url": url
        }
        
        raw_data = self.execute_query(url, params, use_cache=False)
        
        # Process and standardize the result
        business = self._extract_business_details(raw_data)
        
        # Save to cache if result was found
        if business:
            self._save_to_cache(cache_key, business)
            
        return business
    
    def search_by_location(self, 
                          category: str, 
                          location: str,
                          radius_km: float = 5.0,
                          limit: int = 20,
                          use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for businesses near a specific location.
        
        Args:
            category: Business category (e.g., "restaurants", "hotels")
            location: Location to search near (e.g., "Kuala Lumpur")
            radius_km: Search radius in kilometers
            limit: Maximum number of results to return
            use_cache: Whether to use cached results if available
            
        Returns:
            List of standardized business data
        """
        # Construct the full search query
        full_query = f"{category} near {location}"
            
        # Generate a cache key
        cache_key = f"nearby_{hashlib.md5(full_query.encode()).hexdigest()}_{radius_km}_{limit}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved Google Maps nearby search results from cache for '{full_query}'")
                return cached_data
        
        # Construct the Google Maps search URL
        encoded_query = urllib.parse.quote_plus(full_query)
        url = f"https://www.google.com/maps/search/{encoded_query}"
        
        # Execute the query
        params = {
            "url": url
        }
        
        raw_data = self.execute_query(url, params, use_cache=False)
        
        # Process and standardize the results
        businesses = self._extract_businesses(raw_data, limit)
        
        # Save to cache if results were found
        if businesses:
            self._save_to_cache(cache_key, businesses)
            
        return businesses
        
    def execute_query(self, 
                     query: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the Google Maps API.
        
        Args:
            query: The query identifier (typically a URL)
            params: Additional parameters for the query
            use_cache: Whether to use cached results (handled by calling methods)
            
        Returns:
            API response data
        """
        # Apply rate limiting
        self._apply_rate_limiting()
        
        if not self.api_endpoint:
            logger.error("API endpoint not configured for Google Maps client")
            return {"error": "API endpoint not configured"}
        
        try:
            # Here we would make the actual API call to the MCP-powered Actor
            # For now, return a placeholder response
            logger.info(f"Executing Google Maps query for: '{query}'")
            
            # Placeholder - Replace with actual MCP API call
            # return requests.post(self.api_endpoint, json=params).json()
            
            # Determine if this is a place details query or a search query
            if "place_id:" in query:
                # Place details query
                place_id = query.split("place_id:")[1].strip()
                return self._generate_mock_place_details(place_id)
            else:
                # Search query
                search_term = query.split("/search/")[1] if "/search/" in query else query
                search_term = urllib.parse.unquote_plus(search_term)
                return self._generate_mock_search_results(search_term)
            
        except Exception as e:
            logger.error(f"Error executing Google Maps query: {e}")
            return {"error": str(e)}
    
    def _extract_businesses(self, 
                           raw_data: Dict[str, Any], 
                           limit: int) -> List[Dict[str, Any]]:
        """
        Extract businesses from the raw API response.
        
        Args:
            raw_data: Raw data from the Google Maps API
            limit: Maximum number of businesses to extract
            
        Returns:
            List of standardized business data
        """
        businesses = []
        
        # Extract business data from search results
        if raw_data and "results" in raw_data:
            for result in raw_data["results"][:limit]:
                business = self.standardize_to_lead(result)
                if business:
                    businesses.append(business)
        
        logger.info(f"Extracted {len(businesses)} businesses from Google Maps data")
        return businesses
    
    def _extract_business_details(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract detailed business information from the raw API response.
        
        Args:
            raw_data: Raw data from the Google Maps API
            
        Returns:
            Standardized business data or None if not found
        """
        if not raw_data or "place" not in raw_data:
            logger.warning("No valid business details data found")
            return None
            
        return self.standardize_to_lead(raw_data["place"])
    
    def _extract_contact_info(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract contact information from business data.
        
        Args:
            data: Business data from Google Maps
            
        Returns:
            Dictionary with extracted contact information
        """
        contact_info = {
            "phone": "",
            "website": "",
            "email": "",
            "address": ""
        }
        
        # Extract phone number
        if "phoneNumber" in data:
            contact_info["phone"] = data["phoneNumber"]
            
        # Extract website
        if "website" in data:
            contact_info["website"] = data["website"]
            
        # Extract address
        if "formattedAddress" in data:
            contact_info["address"] = data["formattedAddress"]
            
        # Extract email from description or reviews if available
        if "description" in data:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, data["description"], re.IGNORECASE)
            if email_matches:
                contact_info["email"] = email_matches[0]
                
        return contact_info
    
    def _generate_mock_search_results(self, search_term: str) -> Dict[str, Any]:
        """Generate mock search results for testing purposes."""
        # Extract the category and location from the search term
        parts = search_term.lower().split(" in " if " in " in search_term else " near ")
        category = parts[0] if len(parts) > 0 else "business"
        location = parts[1] if len(parts) > 1 else "Kuala Lumpur"
        
        # Generate results based on the search term
        results = []
        for i in range(10):  # Generate 10 mock results
            business_id = f"{hashlib.md5((category + str(i)).encode()).hexdigest()[:8]}"
            
            result = {
                "place_id": f"place_{business_id}",
                "name": f"{category.title()} {['Express', 'Pro', 'Hub', 'Solutions', 'Group'][i % 5]} {i+1}",
                "formattedAddress": f"{i+1} Jalan {category.title()}, {location.title()}, 50000, Malaysia",
                "location": {
                    "lat": 3.1390 + (i * 0.01),
                    "lng": 101.6869 + (i * 0.01)
                },
                "rating": (i % 5) + 1,  # 1-5 rating
                "userRatingsTotal": (i + 1) * 10,  # Number of ratings
                "phoneNumber": f"+60123456{i:03d}",
                "website": f"https://www.{category.lower().replace(' ', '')}{i+1}.com.my",
                "businessStatus": "OPERATIONAL",
                "openingHours": {
                    "weekdayText": [
                        "Monday: 9:00 AM – 6:00 PM",
                        "Tuesday: 9:00 AM – 6:00 PM",
                        "Wednesday: 9:00 AM – 6:00 PM",
                        "Thursday: 9:00 AM – 6:00 PM",
                        "Friday: 9:00 AM – 6:00 PM",
                        "Saturday: 10:00 AM – 4:00 PM",
                        "Sunday: Closed"
                    ]
                },
                "types": [category.lower().replace(" ", "_"), "point_of_interest", "establishment"],
                "description": f"Leading {category} provider in {location}. Contact us at info@{category.lower().replace(' ', '')}{i+1}.com.my for more information.",
                "priceLevel": i % 4  # 0-3 price level
            }
            results.append(result)
            
        return {"results": results}
    
    def _generate_mock_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Generate mock place details for testing purposes.
        
        Args:
            place_id (str): The place ID to generate mock details for.
            
        Returns:
            dict: Mock place details data.
        """
        logger.info(f"Generating mock place details for place ID: {place_id}")
        return {
            "name": f"Business {place_id}",
            "place_id": place_id,
            "formattedAddress": "123 Test Street, Test City",
            "phoneNumber": "+60123456789",
            "website": f"https://www.business-{place_id}.com",
            "description": f"This is a mock business description for {place_id}. Contact us at info@business-{place_id}.com",
            "rating": 4.5,
            "userRatingsTotal": 100,
            "priceLevel": 2,
            "types": ["business", "establishment"],
            "location": {"lat": 3.1390, "lng": 101.6869},
            "openingHours": {
                "weekdayText": [
                    "Monday: 9:00 AM – 6:00 PM",
                    "Tuesday: 9:00 AM – 6:00 PM",
                    "Wednesday: 9:00 AM – 6:00 PM",
                    "Thursday: 9:00 AM – 6:00 PM",
                    "Friday: 9:00 AM – 6:00 PM",
                    "Saturday: 10:00 AM – 4:00 PM",
                    "Sunday: Closed"
                ]
            }
        }
    
    def _clear_cache(self):
        """
        Clear all cached files in the cache directory.
        Only used for testing purposes.
        
        Returns:
            None
        """
        if not os.path.exists(self.cache_dir):
            return
            
        logger.info(f"Clearing cache in directory: {self.cache_dir}")
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                    logger.debug(f"Removed cache file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing cache file {file_path}: {str(e)}")
    
    def standardize_to_lead(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize Google Maps business data to the common lead format.
        
        Args:
            business_data: Google Maps business data
            
        Returns:
            Standardized lead data dictionary
        """
        if not business_data:
            logger.warning("No business data to standardize")
            return {}
            
        # Extract contact information
        contact_info = self._extract_contact_info(business_data)
        
        # Extract business types/categories
        categories = business_data.get("types", [])
        primary_category = categories[0].replace("_", " ").title() if categories else ""
        
        # Standardize the data
        lead = {
            "organization": business_data.get("name", ""),
            "person_name": "",  # Google Maps doesn't typically provide a contact person
            "role": "",         # Role not typically provided
            "email": contact_info.get("email", ""),
            "phone": contact_info.get("phone", ""),
            "address": contact_info.get("address", ""),
            "website": contact_info.get("website", ""),
            "source_url": f"https://www.google.com/maps/place/?q=place_id:{business_data.get('place_id', '')}",
            "source_type": "google_maps",
            "metadata": {
                "place_id": business_data.get("place_id", ""),
                "category": primary_category,
                "categories": categories,
                "rating": business_data.get("rating", 0),
                "reviews_count": business_data.get("userRatingsTotal", 0),
                "price_level": business_data.get("priceLevel", 0),
                "location_coordinates": business_data.get("location", {}),
                "business_status": business_data.get("businessStatus", ""),
                "opening_hours": business_data.get("openingHours", {}).get("weekdayText", []),
                "description": business_data.get("description", ""),
                "raw_data": business_data
            }
        }
        
        logger.info(f"Standardized Google Maps business to lead format: {business_data.get('name', '')}")
        return lead 