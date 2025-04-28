"""
Instagram client adapter for MCP-powered Apify Actor integration.

This module provides a client adapter for the Instagram Scraper Apify Actor,
allowing extraction of business data from Instagram profiles and posts.
"""

import time
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base_client import (
    BaseApiClient, 
    ApiConnectionError,
    ApiResponseError,
    ApiTimeoutError,
    ApiRateLimitError,
    ApiConfigurationError
)

# Set up logging
logger = logging.getLogger(__name__)

class InstagramClient(BaseApiClient):
    """Client for Instagram Scraper Apify Actor integration."""
    
    def __init__(self, 
                api_endpoint: str,
                cache_dir: str = "cache/instagram",
                cache_ttl: int = 86400,
                timeout: int = 60,
                max_retries: int = 3,
                retry_delay: int = 5):
        """
        Initialize the Instagram client.
        
        Args:
            api_endpoint: URL of the Instagram Scraper API endpoint
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        super().__init__(cache_dir=cache_dir, cache_ttl=cache_ttl)
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = 2.0  # Seconds between requests
        
        logger.info(f"Instagram client initialized with endpoint: {api_endpoint}")
    
    def execute_query(self, 
                     query: str, 
                     params: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a query against the Instagram Scraper API.
        
        Args:
            query: Instagram username, hashtag, or URL to query
            params: Additional parameters for the query
            use_cache: Whether to use cached results if available
            
        Returns:
            API response data
        """
        if not self.api_endpoint:
            raise ApiConfigurationError("Instagram API endpoint not configured")
        
        # Build request parameters
        request_params = {
            "directUrls": [query] if query.startswith("https://") else None,
            "search": None if query.startswith("https://") else query,
            "searchType": "user" if query.startswith("@") else "hashtag",
            "resultsLimit": params.get("limit", 20) if params else 20,
            "resultsType": params.get("results_type", "posts") if params else "posts"
        }
        
        # Clean up parameters
        if request_params["directUrls"] is None:
            del request_params["directUrls"]
        if request_params["search"] is None:
            del request_params["search"]
        
        # If search is a username and starts with @, remove it
        if "search" in request_params and request_params["search"].startswith("@"):
            request_params["search"] = request_params["search"][1:]
            
        # Generate cache key
        cache_key = f"instagram_{query}_{json.dumps(request_params, sort_keys=True)}"
        
        # Try to get from cache if enabled
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Retrieved Instagram data from cache for: {query}")
                return cached_data
        
        # Apply rate limiting
        self._apply_rate_limiting()
        
        # Make the API request with retries
        response_data = None
        retries = 0
        
        while retries <= self.max_retries:
            try:
                logger.info(f"Querying Instagram API for: {query}")
                
                response = requests.post(
                    self.api_endpoint,
                    json=request_params,
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay * 2))
                    raise ApiRateLimitError(
                        f"Instagram API rate limit exceeded, retry after {retry_after} seconds",
                        retry_after=retry_after
                    )
                
                if response.status_code == 401 or response.status_code == 403:
                    # Authentication error
                    error_msg = response.json().get("error", "Authentication failed")
                    logger.error(f"Instagram API authentication error: {error_msg}")
                    raise ApiConnectionError(f"Instagram API authentication error: {error_msg}")
                
                if response.status_code != 200:
                    # Other API errors
                    error_msg = response.json().get("error", f"API error: {response.status_code}")
                    logger.error(f"Instagram API error: {error_msg}")
                    raise ApiResponseError(
                        f"Instagram API error: {error_msg}",
                        status_code=response.status_code,
                        response_data=response.json() if response.content else None
                    )
                
                # Parse response data
                response_data = response.json()
                break
                
            except requests.exceptions.Timeout:
                logger.warning(f"Instagram API request timeout, retrying ({retries+1}/{self.max_retries})")
                retries += 1
                if retries > self.max_retries:
                    raise ApiTimeoutError(f"Instagram API request timed out after {self.max_retries} retries")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Instagram API request error: {e}, retrying ({retries+1}/{self.max_retries})")
                retries += 1
                if retries > self.max_retries:
                    raise ApiConnectionError(f"Instagram API connection error: {e}")
                time.sleep(self.retry_delay)
                
            except ApiRateLimitError as e:
                logger.warning(f"Instagram API rate limit error: {e}")
                retries += 1
                if retries > self.max_retries:
                    raise
                time.sleep(e.retry_after or self.retry_delay * 2)
        
        if response_data:
            # Save to cache
            self._save_to_cache(cache_key, response_data)
            logger.info(f"Successfully retrieved Instagram data for: {query}")
            return response_data
        else:
            raise ApiConnectionError(f"Failed to get data from Instagram API for: {query}")
    
    def get_profile(self, username: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get information about an Instagram profile.
        
        Args:
            username: Instagram username (with or without @)
            use_cache: Whether to use cached results if available
            
        Returns:
            Profile information
        """
        # Clean username format (ensure it has @ prefix)
        if not username.startswith('@'):
            username = f"@{username}"
            
        params = {
            "results_type": "details",
            "limit": 1
        }
        
        raw_data = self.execute_query(username, params, use_cache)
        
        # If response is empty or doesn't contain profile data
        if not raw_data or not raw_data.get("graphql", {}).get("user"):
            logger.warning(f"No profile data found for Instagram user: {username}")
            return {}
            
        return self._extract_profile_data(raw_data)
    
    def get_profile_posts(self, 
                         username: str, 
                         limit: int = 20, 
                         use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get posts from an Instagram profile.
        
        Args:
            username: Instagram username (with or without @)
            limit: Maximum number of posts to retrieve
            use_cache: Whether to use cached results if available
            
        Returns:
            List of posts
        """
        # Clean username format (ensure it has @ prefix)
        if not username.startswith('@'):
            username = f"@{username}"
            
        params = {
            "results_type": "posts",
            "limit": limit
        }
        
        raw_data = self.execute_query(username, params, use_cache)
        
        # If response is empty or doesn't contain posts
        if not raw_data or "data" not in raw_data:
            logger.warning(f"No posts found for Instagram user: {username}")
            return []
            
        return self._extract_posts_data(raw_data)
    
    def search_hashtag(self, 
                      hashtag: str, 
                      limit: int = 20, 
                      use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search Instagram for posts with a specific hashtag.
        
        Args:
            hashtag: Hashtag to search for (with or without #)
            limit: Maximum number of posts to retrieve
            use_cache: Whether to use cached results if available
            
        Returns:
            List of posts with the hashtag
        """
        # Clean hashtag format (remove # if present)
        if hashtag.startswith('#'):
            hashtag = hashtag[1:]
            
        params = {
            "results_type": "posts",
            "limit": limit
        }
        
        raw_data = self.execute_query(hashtag, params, use_cache)
        
        # If response is empty or doesn't contain posts
        if not raw_data or "data" not in raw_data:
            logger.warning(f"No posts found for Instagram hashtag: #{hashtag}")
            return []
            
        return self._extract_posts_data(raw_data)
    
    def search_business(self, 
                       location: str, 
                       category: Optional[str] = None,
                       limit: int = 20, 
                       use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search Instagram for business profiles in a specific location.
        
        Args:
            location: Location to search in (e.g., "Kuala Lumpur")
            category: Business category to filter by
            limit: Maximum number of profiles to retrieve
            use_cache: Whether to use cached results if available
            
        Returns:
            List of business profiles
        """
        search_query = location
        if category:
            search_query = f"{category} {location}"
            
        params = {
            "searchType": "place",
            "resultsType": "details",
            "limit": limit
        }
        
        raw_data = self.execute_query(search_query, params, use_cache)
        
        # If response is empty or doesn't contain profiles
        if not raw_data or "graphql" not in raw_data:
            logger.warning(f"No business profiles found for Instagram search: {search_query}")
            return []
            
        return self._extract_business_data(raw_data)
    
    def _extract_profile_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure profile data from API response.
        
        Args:
            raw_data: Raw API response data
            
        Returns:
            Structured profile data
        """
        try:
            user_data = raw_data.get("graphql", {}).get("user", {})
            if not user_data:
                return {}
                
            # Extract business contact information
            business_info = user_data.get("business_address_json", {})
            business_email = user_data.get("business_email", "")
            business_phone = user_data.get("business_phone_number", "")
            business_category = user_data.get("category_name", "")
            
            # Build structured profile data
            profile_data = {
                "username": user_data.get("username", ""),
                "full_name": user_data.get("full_name", ""),
                "biography": user_data.get("biography", ""),
                "followers_count": user_data.get("edge_followed_by", {}).get("count", 0),
                "following_count": user_data.get("edge_follow", {}).get("count", 0),
                "post_count": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
                "is_business_account": user_data.get("is_business_account", False),
                "is_verified": user_data.get("is_verified", False),
                "external_url": user_data.get("external_url", ""),
                "profile_pic_url": user_data.get("profile_pic_url_hd", ""),
                "business_category": business_category,
                "email": business_email,
                "phone": business_phone,
                "address": business_info.get("street_address", ""),
                "city": business_info.get("city_name", ""),
                "zip_code": business_info.get("zip_code", ""),
                "website": user_data.get("external_url", ""),
                "data_source": "instagram"
            }
            
            return profile_data
        except Exception as e:
            logger.error(f"Error extracting Instagram profile data: {e}")
            return {}
    
    def _extract_posts_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and structure posts data from API response.
        
        Args:
            raw_data: Raw API response data
            
        Returns:
            List of structured post data
        """
        try:
            posts_data = []
            posts = raw_data.get("data", [])
            
            for post in posts:
                # Extract post details
                post_data = {
                    "post_id": post.get("id", ""),
                    "shortcode": post.get("shortcode", ""),
                    "caption": post.get("caption", ""),
                    "likes_count": post.get("likes", 0),
                    "comments_count": post.get("comments", 0),
                    "timestamp": post.get("timestamp", ""),
                    "url": f"https://www.instagram.com/p/{post.get('shortcode', '')}",
                    "image_url": post.get("display_url", ""),
                    "location": post.get("location", {}).get("name", ""),
                    "is_video": post.get("is_video", False),
                    "video_url": post.get("video_url", ""),
                    "hashtags": self._extract_hashtags(post.get("caption", "")),
                    "mentions": self._extract_mentions(post.get("caption", "")),
                    "tagged_users": post.get("tagged_users", [])
                }
                
                posts_data.append(post_data)
                
            return posts_data
        except Exception as e:
            logger.error(f"Error extracting Instagram posts data: {e}")
            return []
    
    def _extract_business_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and structure business data from API response.
        
        Args:
            raw_data: Raw API response data
            
        Returns:
            List of structured business data
        """
        try:
            businesses_data = []
            places = raw_data.get("places", [])
            
            for place in places:
                # Extract business details
                business_data = {
                    "place_id": place.get("id", ""),
                    "name": place.get("name", ""),
                    "slug": place.get("slug", ""),
                    "address": place.get("location", {}).get("address", ""),
                    "city": place.get("location", {}).get("city", ""),
                    "lat": place.get("location", {}).get("lat", 0),
                    "lng": place.get("location", {}).get("lng", 0),
                    "website": place.get("website", ""),
                    "phone": place.get("phone", ""),
                    "category": place.get("category", ""),
                    "profile_pic_url": place.get("profile_pic_url", ""),
                    "data_source": "instagram"
                }
                
                businesses_data.append(business_data)
                
            return businesses_data
        except Exception as e:
            logger.error(f"Error extracting Instagram business data: {e}")
            return []
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Text to extract hashtags from
            
        Returns:
            List of hashtags
        """
        if not text:
            return []
            
        import re
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)
        return hashtags
    
    def _extract_mentions(self, text: str) -> List[str]:
        """
        Extract mentions from text.
        
        Args:
            text: Text to extract mentions from
            
        Returns:
            List of mentions
        """
        if not text:
            return []
            
        import re
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)
        return mentions
    
    def _standardize_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Standardize API response data to a common lead format.
        
        Args:
            raw_data: Raw data from the API
            
        Returns:
            Standardized list of lead data dictionaries
        """
        standardized_leads = []
        
        # Handle profile data
        if raw_data.get("graphql", {}).get("user", {}):
            profile_data = self._extract_profile_data(raw_data)
            
            if profile_data:
                lead = {
                    "company_name": profile_data.get("full_name", ""),
                    "contact_name": profile_data.get("full_name", ""),
                    "email": profile_data.get("email", ""),
                    "phone": profile_data.get("phone", ""),
                    "address": profile_data.get("address", ""),
                    "city": profile_data.get("city", ""),
                    "zip_code": profile_data.get("zip_code", ""),
                    "website": profile_data.get("website", ""),
                    "industry": profile_data.get("business_category", ""),
                    "source": "Instagram",
                    "social_media": {
                        "instagram": f"https://www.instagram.com/{profile_data.get('username', '')}"
                    },
                    "notes": profile_data.get("biography", ""),
                    "followers": profile_data.get("followers_count", 0),
                    "raw_data": profile_data
                }
                
                standardized_leads.append(lead)
        
        # Handle business search data
        elif raw_data.get("places", []):
            businesses = self._extract_business_data(raw_data)
            
            for business in businesses:
                lead = {
                    "company_name": business.get("name", ""),
                    "contact_name": "",
                    "email": "",
                    "phone": business.get("phone", ""),
                    "address": business.get("address", ""),
                    "city": business.get("city", ""),
                    "website": business.get("website", ""),
                    "industry": business.get("category", ""),
                    "source": "Instagram",
                    "social_media": {},
                    "notes": f"Found via Instagram location search",
                    "raw_data": business
                }
                
                standardized_leads.append(lead)
        
        return standardized_leads 