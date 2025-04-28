"""
RAG Web Browser client for MCP-powered Apify Actor integration.

This module provides a client to interact with the rag-web-browser
MCP-powered Apify Actor, which performs Google searches and extracts
content from websites.
"""

import logging
import json
import hashlib
import re
from typing import Dict, Any, List, Optional, Union
import requests

from .base_client import BaseApiClient

# Set up logging
logger = logging.getLogger(__name__)

class WebBrowserClient(BaseApiClient):
    """Client for interacting with the RAG Web Browser MCP-powered Actor."""
    
    def __init__(self, 
                api_endpoint: str = None,
                cache_dir: str = "cache/web_browser", 
                cache_ttl: int = 86400):
        """
        Initialize the RAG Web Browser client.
        
        Args:
            api_endpoint: The MCP-powered API endpoint (from Cursor)
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(cache_dir, cache_ttl)
        self.api_endpoint = api_endpoint
        self.rate_limit_delay = 5.0  # Longer delay for web searches
        logger.info("Initialized RAG Web Browser client")
        
    def search_and_extract(self, 
                          query: str, 
                          max_results: int = 3,
                          output_format: str = "markdown",
                          use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Perform a search and extract content from the top results.
        
        Args:
            query: Search query
            max_results: Maximum number of search results to process
            output_format: Format for the extracted content (markdown, text, html)
            use_cache: Whether to use cached results if available
            
        Returns:
            List of search results with extracted content
        """
        # Generate a cache key
        cache_key = f"web_{hashlib.md5(query.encode()).hexdigest()}_{max_results}_{output_format}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved web search results from cache for '{query}'")
                return self._standardize_data(cached_data)
        
        # Execute the query
        params = {
            "query": query,
            "maxResults": max_results,
            "outputFormats": [output_format]
        }
        
        raw_data = self.execute_query(query, params, use_cache=False)
        
        # Save to cache if results were found
        if raw_data and not raw_data.get("error"):
            self._save_to_cache(cache_key, raw_data)
            
        # Standardize and return the data
        return self._standardize_data(raw_data)
    
    def extract_from_url(self, 
                        url: str, 
                        output_format: str = "markdown",
                        use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Extract content from a specific URL.
        
        Args:
            url: The URL to extract content from
            output_format: Format for the extracted content (markdown, text, html)
            use_cache: Whether to use cached results if available
            
        Returns:
            Extracted content data or None if extraction failed
        """
        # Generate a cache key
        cache_key = f"url_{hashlib.md5(url.encode()).hexdigest()}_{output_format}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved URL extraction from cache for '{url}'")
                results = self._standardize_data(cached_data)
                return results[0] if results else None
        
        # Execute the query
        params = {
            "query": url,  # URL is passed as the query
            "outputFormats": [output_format]
        }
        
        raw_data = self.execute_query(url, params, use_cache=False)
        
        # Save to cache if results were found
        if raw_data and not raw_data.get("error"):
            self._save_to_cache(cache_key, raw_data)
            
        # Standardize and return the data
        results = self._standardize_data(raw_data)
        return results[0] if results else None
    
    def search_for_business(self, 
                            business_name: str, 
                            location: Optional[str] = None,
                            use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for a specific business and extract contact information.
        
        Args:
            business_name: Name of the business
            location: Optional location to focus search (e.g., "Kuala Lumpur")
            use_cache: Whether to use cached results if available
            
        Returns:
            List of business data with extracted contact information
        """
        # Construct a targeted search query
        query = business_name
        if location:
            query = f"{business_name} {location} contact information"
        else:
            query = f"{business_name} malaysia contact information"
            
        # Perform the search
        search_results = self.search_and_extract(query, max_results=3, use_cache=use_cache)
        
        # Extract business information from the search results
        enhanced_results = []
        for result in search_results:
            # Extract email and phone from content if not already present
            if not result.get("email") or not result.get("phone"):
                extracted_info = self._extract_contact_info(result.get("content", ""))
                
                if not result.get("email") and extracted_info.get("email"):
                    result["email"] = extracted_info["email"]
                    
                if not result.get("phone") and extracted_info.get("phone"):
                    result["phone"] = extracted_info["phone"]
                    
                if not result.get("address") and extracted_info.get("address"):
                    result["address"] = extracted_info["address"]
            
            enhanced_results.append(result)
            
        return enhanced_results
    
    def execute_query(self, 
                     query: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the RAG Web Browser API.
        
        Args:
            query: The search query or URL
            params: Additional parameters for the query
            use_cache: Whether to use cached results (handled by calling methods)
            
        Returns:
            API response data
        """
        # Apply rate limiting
        self._apply_rate_limiting()
        
        if not self.api_endpoint:
            logger.error("API endpoint not configured for RAG Web Browser client")
            return {"error": "API endpoint not configured"}
        
        try:
            # Here we would make the actual API call to the MCP-powered Actor
            # For now, return a placeholder response
            logger.info(f"Executing RAG Web Browser query for: '{query}'")
            
            # Placeholder - Replace with actual MCP API call
            # return requests.post(self.api_endpoint, json=params).json()
            
            # Placeholder response - simulate a search for Malaysian businesses
            if query.startswith(("http://", "https://")):
                # URL extraction
                return {
                    "url": query,
                    "title": "Example Business Website",
                    "content": """
                    # Example Business Malaysia
                    
                    Welcome to Example Business, a leading consulting firm in Malaysia.
                    
                    ## Contact Information
                    
                    - Email: info@examplebusiness.com.my
                    - Phone: +60123456789
                    - Address: 123 Jalan Example, 50000 Kuala Lumpur, Malaysia
                    
                    ## Our Services
                    
                    We provide a wide range of consulting services for businesses in Malaysia.
                    """
                }
            else:
                # Search results
                return {
                    "query": query,
                    "results": [
                        {
                            "url": "https://www.example1.com.my",
                            "title": "Example Business 1 | Leading Consulting in Malaysia",
                            "content": """
                            # Example Business 1
                            
                            A premier consulting firm in Kuala Lumpur, Malaysia.
                            
                            ## Contact Us
                            
                            Email: info@example1.com.my
                            Phone: +60123456789
                            Address: 123 Jalan Sultan, 50000 Kuala Lumpur, Malaysia
                            
                            ## Our Services
                            
                            - Business Strategy
                            - Digital Transformation
                            - Financial Advisory
                            """
                        },
                        {
                            "url": "https://www.example2.com.my",
                            "title": "Example Business 2 | Malaysian Engineering Consultants",
                            "content": """
                            # Example Business 2
                            
                            Engineering consultants based in Penang, Malaysia.
                            
                            ## How to Reach Us
                            
                            Send inquiries to: contact@example2.com.my
                            Call us: +60123456780
                            Visit: 456 Jalan Penang, 10000 Penang, Malaysia
                            
                            ## Our Engineering Expertise
                            
                            - Structural Engineering
                            - Environmental Consulting
                            - Project Management
                            """
                        }
                    ]
                }
            
        except Exception as e:
            logger.error(f"Error executing RAG Web Browser query: {e}")
            return {"error": str(e)}
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information from text content.
        
        Args:
            text: The text content to analyze
            
        Returns:
            Dictionary with extracted email, phone, and address
        """
        # Simple regex patterns for email and phone
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # Malaysian phone pattern
        phone_pattern = r'(?:\+?60|0)1[0-46-9][\s-]?\d{3,4}[\s-]?\d{3,4}'
        # Simple address pattern for Malaysian addresses
        address_pattern = r'\d+\s+Jalan\s+[A-Za-z0-9\s,]+(?:Kuala Lumpur|Penang|Johor|Selangor|Sabah|Sarawak|Perak|Melaka|Negeri Sembilan|Pahang|Terengganu|Kelantan|Putrajaya|Labuan|Perlis|Kedah|Malaysia)[A-Za-z0-9\s,]*\d{5}'
        
        contact_info = {
            "email": "",
            "phone": "",
            "address": ""
        }
        
        # Extract email
        email_matches = re.findall(email_pattern, text, re.IGNORECASE)
        if email_matches:
            contact_info["email"] = email_matches[0]
            
        # Extract phone
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            contact_info["phone"] = phone_matches[0]
            
        # Extract address
        address_matches = re.findall(address_pattern, text, re.IGNORECASE)
        if address_matches:
            contact_info["address"] = address_matches[0].strip()
            
        return contact_info
    
    def _standardize_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Standardize RAG Web Browser data to the common lead format.
        
        Args:
            raw_data: Raw data from the RAG Web Browser API
            
        Returns:
            Standardized list of lead data dictionaries
        """
        if not raw_data or raw_data.get("error"):
            logger.warning("No valid data to standardize from RAG Web Browser")
            return []
            
        standardized_leads = []
        
        # Process URL extraction result
        if "url" in raw_data and "content" in raw_data:
            # Single URL extraction
            content = raw_data.get("content", "")
            contact_info = self._extract_contact_info(content)
            
            # Try to extract organization name from title
            organization = raw_data.get("title", "").split(" | ")[0].strip()
            
            lead = {
                "organization": organization,
                "person_name": "",
                "role": "",
                "email": contact_info.get("email", ""),
                "phone": contact_info.get("phone", ""),
                "address": contact_info.get("address", ""),
                "website": raw_data.get("url", ""),
                "source_url": raw_data.get("url", ""),
                "source_type": "website",
                "metadata": {
                    "title": raw_data.get("title", ""),
                    "content": content,
                    "raw_data": raw_data
                }
            }
            standardized_leads.append(lead)
            
        # Process search results
        elif "results" in raw_data:
            # Multiple search results
            for result in raw_data["results"]:
                content = result.get("content", "")
                contact_info = self._extract_contact_info(content)
                
                # Try to extract organization name from title
                organization = result.get("title", "").split(" | ")[0].strip()
                
                lead = {
                    "organization": organization,
                    "person_name": "",
                    "role": "",
                    "email": contact_info.get("email", ""),
                    "phone": contact_info.get("phone", ""),
                    "address": contact_info.get("address", ""),
                    "website": result.get("url", ""),
                    "source_url": result.get("url", ""),
                    "source_type": "website",
                    "metadata": {
                        "title": result.get("title", ""),
                        "content": content,
                        "raw_data": result
                    }
                }
                standardized_leads.append(lead)
                
        logger.info(f"Standardized {len(standardized_leads)} leads from RAG Web Browser data")
        return standardized_leads 