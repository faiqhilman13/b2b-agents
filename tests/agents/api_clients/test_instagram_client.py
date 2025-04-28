"""
Tests for the Instagram API client integration.
"""

import pytest
from unittest.mock import patch, MagicMock, ANY
import json
import os
import responses

from lead_generator.agents.api_clients.instagram_client import InstagramClient
from lead_generator.agents.api_clients.base_client import (
    ApiResponseError,
    ApiConnectionError
)

# Test constants
MOCK_API_ENDPOINT = "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync"
MOCK_API_KEY = "test_api_key"

# Sample response fixtures
SAMPLE_PROFILE_RESPONSE = {
    "data": [
        {
            "id": "12345",
            "username": "test_business",
            "fullName": "Test Business Account",
            "biography": "Business account for testing. Contact us at test@example.com or +601234567890",
            "followersCount": 1000,
            "followsCount": 500,
            "profilePicUrl": "https://example.com/pic.jpg",
            "externalUrl": "https://www.testbusiness.com",
            "business": True,
            "businessCategoryName": "Software Company",
            "verified": True
        }
    ]
}

SAMPLE_POSTS_RESPONSE = {
    "data": [
        {
            "id": "post123",
            "caption": "Check out our new product! Contact us at sales@example.com",
            "commentsCount": 25,
            "likesCount": 150,
            "hashtags": ["tech", "product", "launch"],
            "mentions": ["partner_company"],
            "url": "https://www.instagram.com/p/post123/",
            "timestamp": "2023-08-15T10:30:00Z",
            "type": "Image",
            "locationName": "Kuala Lumpur, Malaysia"
        },
        {
            "id": "post456",
            "caption": "Visit our website at www.testbusiness.com or call us at +601987654321",
            "commentsCount": 10,
            "likesCount": 75,
            "url": "https://www.instagram.com/p/post456/",
            "timestamp": "2023-08-10T14:15:00Z",
            "type": "Video"
        }
    ]
}

@pytest.fixture
def instagram_client():
    """Fixture to create a test Instagram client."""
    with patch.dict(os.environ, {"APIFY_API_KEY": MOCK_API_KEY}):
        client = InstagramClient(api_endpoint=MOCK_API_ENDPOINT)
        return client


class TestInstagramClient:
    """Test cases for the Instagram API client."""

    @responses.activate
    def test_get_profile_success(self, instagram_client):
        """Test successful profile retrieval."""
        # Mock the API response
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=SAMPLE_PROFILE_RESPONSE,
            status=200
        )

        # Test the method
        profile_data = instagram_client.get_profile("test_business")

        # Assertions
        assert profile_data["username"] == "test_business"
        assert profile_data["business"] == True
        assert "testbusiness.com" in profile_data["website"]
        assert "test@example.com" in profile_data["contact_info"]
        assert "+601234567890" in profile_data["contact_info"]

    @responses.activate
    def test_get_profile_posts_success(self, instagram_client):
        """Test successful retrieval of profile posts."""
        # Mock the API response
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=SAMPLE_POSTS_RESPONSE,
            status=200
        )

        # Test the method
        posts_data = instagram_client.get_profile_posts("test_business")

        # Assertions
        assert len(posts_data) == 2
        assert "sales@example.com" in posts_data[0]["contact_info"]
        assert "www.testbusiness.com" in posts_data[1]["contact_info"]
        assert "+601987654321" in posts_data[1]["contact_info"]
        assert "Kuala Lumpur, Malaysia" in posts_data[0]["location"]

    @responses.activate
    def test_search_business_success(self, instagram_client):
        """Test successful business search."""
        # Mock the profile API response
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=SAMPLE_PROFILE_RESPONSE,
            status=200
        )
        
        # Mock the posts API response (second call)
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=SAMPLE_POSTS_RESPONSE,
            status=200
        )

        # Test the method
        business_data = instagram_client.search_business("Test Business Malaysia")

        # Assertions
        assert business_data["name"] == "Test Business Account"
        assert business_data["category"] == "Software Company"
        assert "test@example.com" in business_data["contact_info"]
        assert "+601234567890" in business_data["contact_info"]
        assert "sales@example.com" in business_data["contact_info"]
        assert "+601987654321" in business_data["contact_info"]
        assert "Kuala Lumpur, Malaysia" in business_data["locations"]
        assert business_data["verified"] == True

    @responses.activate
    def test_search_hashtag_success(self, instagram_client):
        """Test successful hashtag search."""
        # Mock the API response for hashtag search
        hashtag_response = {
            "data": [
                {
                    "id": "tag123",
                    "name": "malaysiatech",
                    "count": 5000,
                    "url": "https://www.instagram.com/explore/tags/malaysiatech/"
                }
            ]
        }
        
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=hashtag_response,
            status=200
        )
        
        # Mock the posts API response
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json=SAMPLE_POSTS_RESPONSE,
            status=200
        )

        # Test the method
        results = instagram_client.search_hashtag("malaysiatech")

        # Assertions
        assert len(results) > 0
        assert "Test Business Account" in str(results)
        assert "sales@example.com" in str(results)

    @responses.activate
    def test_api_error_handling(self, instagram_client):
        """Test error handling for API failures."""
        # Mock an API error response
        responses.add(
            responses.POST,
            MOCK_API_ENDPOINT,
            json={"error": {"message": "API Error"}},
            status=400
        )

        # Test that the error is properly handled
        with pytest.raises(ApiResponseError):
            instagram_client.get_profile("test_business")

    @patch('requests.post')
    def test_connection_error_handling(self, mock_post, instagram_client):
        """Test handling of connection errors."""
        # Mock a connection error
        mock_post.side_effect = ConnectionError("Connection failed")

        # Test that the error is properly handled
        with pytest.raises(ApiConnectionError):
            instagram_client.get_profile("test_business")

    def test_extract_contact_info(self, instagram_client):
        """Test the extraction of contact info from text."""
        # Test texts
        text1 = "Contact us at info@example.com or call +60123456789"
        text2 = "Visit www.example.com for more information"
        text3 = "Our WhatsApp is +6011-2345-6789 and email: support@example.my"

        # Test the method
        info1 = instagram_client._extract_contact_info(text1)
        info2 = instagram_client._extract_contact_info(text2)
        info3 = instagram_client._extract_contact_info(text3)

        # Assertions
        assert "info@example.com" in info1
        assert "+60123456789" in info1
        
        assert "www.example.com" in info2
        
        assert "+6011-2345-6789" in info3
        assert "support@example.my" in info3 