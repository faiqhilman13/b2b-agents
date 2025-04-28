"""
Tests for the Google Maps client.

This module contains unit tests for the GoogleMapsClient class to ensure
it correctly extracts business information from Google Maps listings.
"""

import os
import pytest
import json
import hashlib
from unittest.mock import patch, MagicMock
from lead_generator.agents.api_clients.gmaps_client import GoogleMapsClient


@pytest.fixture
def gmaps_client():
    """Create a Google Maps client for testing."""
    # Use a temporary directory for cache during tests
    temp_cache_dir = "tests_cache/gmaps"
    os.makedirs(temp_cache_dir, exist_ok=True)
    
    # Create client with test configuration
    client = GoogleMapsClient(
        api_endpoint="https://test-endpoint.example.com/api",
        cache_dir=temp_cache_dir,
        cache_ttl=60  # Short TTL for testing
    )
    
    # Return the configured client
    yield client
    
    # Clean up cache files after tests
    client._clear_cache()
    if os.path.exists(temp_cache_dir):
        for file in os.listdir(temp_cache_dir):
            os.remove(os.path.join(temp_cache_dir, file))
        os.rmdir(temp_cache_dir)


def test_search_businesses(gmaps_client):
    """Test searching for businesses on Google Maps."""
    # Test search
    results = gmaps_client.search_businesses(
        query="coffee shops",
        location="Kuala Lumpur",
        limit=5
    )
    
    # Verify results
    assert isinstance(results, list)
    assert len(results) > 0
    assert len(results) <= 5  # Should respect the limit parameter
    
    # Check standard lead format
    lead = results[0]
    assert "organization" in lead
    assert "email" in lead
    assert "phone" in lead
    assert "website" in lead
    assert "source_type" in lead
    assert lead["source_type"] == "google_maps"
    
    # Check metadata
    assert "metadata" in lead
    assert "place_id" in lead["metadata"]
    assert "category" in lead["metadata"]
    assert "rating" in lead["metadata"]


def test_get_business_details(gmaps_client):
    """Test retrieving detailed information about a business."""
    # Get sample place ID (could be from a search result)
    place_id = "place_test123"
    
    # Get business details
    business = gmaps_client.get_business_details(place_id)
    
    # Verify business data
    assert business is not None
    assert "organization" in business
    assert business["source_type"] == "google_maps"
    assert business["metadata"]["place_id"] == place_id
    
    # Check additional details that should be in detailed view
    assert "opening_hours" in business["metadata"]
    assert "description" in business["metadata"]


def test_search_by_location(gmaps_client):
    """Test searching for businesses near a location."""
    # Search for businesses near a location
    results = gmaps_client.search_by_location(
        category="restaurants",
        location="Kuala Lumpur",
        radius_km=2.0,
        limit=3
    )
    
    # Verify results
    assert isinstance(results, list)
    assert len(results) > 0
    assert len(results) <= 3  # Should respect the limit parameter
    
    # Check standard lead format for each result
    for lead in results:
        assert "organization" in lead
        assert "source_type" in lead
        assert lead["source_type"] == "google_maps"
        
        # The category should match our search
        assert "metadata" in lead
        assert "category" in lead["metadata"]
        assert "restaurant" in lead["metadata"]["category"].lower()


def test_caching_mechanism(gmaps_client):
    """Test that the caching mechanism works correctly."""
    # Mock the internal execute_query method to track calls
    original_execute = gmaps_client.execute_query
    call_count = [0]  # Use list to allow modification in the nested function
    
    def mock_execute(*args, **kwargs):
        call_count[0] += 1
        return original_execute(*args, **kwargs)
    
    gmaps_client.execute_query = mock_execute
    
    try:
        # First call should execute the query
        results1 = gmaps_client.search_businesses(
            query="bakery",
            location="Kuala Lumpur"
        )
        assert call_count[0] == 1
        
        # Second call with same parameters should use cache
        results2 = gmaps_client.search_businesses(
            query="bakery",
            location="Kuala Lumpur"
        )
        assert call_count[0] == 1  # Should not have increased
        
        # Results should be identical
        assert results1 == results2
        
        # Different query should execute a new query
        results3 = gmaps_client.search_businesses(
            query="hotel",
            location="Kuala Lumpur"
        )
        assert call_count[0] == 2
        
        # Verify results are different
        assert results1 != results3
    finally:
        # Restore original method
        gmaps_client.execute_query = original_execute


def test_contact_info_extraction(gmaps_client):
    """Test extraction of contact information from business data."""
    # Create test business data with contact information
    test_data = {
        "name": "Test Business",
        "place_id": "test_place_id",
        "formattedAddress": "123 Test Street, Test City",
        "phoneNumber": "+6012345678",
        "website": "https://www.testbusiness.com",
        "description": "Contact us at info@testbusiness.com for more details."
    }
    
    # Extract contact info
    contact_info = gmaps_client._extract_contact_info(test_data)
    
    # Verify extracted information
    assert contact_info["phone"] == "+6012345678"
    assert contact_info["website"] == "https://www.testbusiness.com"
    assert contact_info["address"] == "123 Test Street, Test City"
    assert contact_info["email"] == "info@testbusiness.com"


def test_standardize_to_lead(gmaps_client):
    """Test standardization of Google Maps data to lead format."""
    # Create test business data
    test_data = {
        "name": "Test Restaurant",
        "place_id": "test_place_id",
        "formattedAddress": "123 Food Street, Test City",
        "phoneNumber": "+6012345678",
        "website": "https://www.testrestaurant.com",
        "description": "Contact us at info@testrestaurant.com",
        "rating": 4.5,
        "userRatingsTotal": 100,
        "priceLevel": 2,
        "types": ["restaurant", "food", "point_of_interest"],
        "location": {"lat": 3.1390, "lng": 101.6869},
        "businessStatus": "OPERATIONAL",
        "openingHours": {
            "weekdayText": [
                "Monday: 9:00 AM – 6:00 PM",
                "Tuesday: 9:00 AM – 6:00 PM",
            ]
        }
    }
    
    # Standardize to lead
    lead = gmaps_client.standardize_to_lead(test_data)
    
    # Verify lead format
    assert lead["organization"] == "Test Restaurant"
    assert lead["email"] == "info@testrestaurant.com"
    assert lead["phone"] == "+6012345678"
    assert lead["website"] == "https://www.testrestaurant.com"
    assert lead["address"] == "123 Food Street, Test City"
    assert lead["source_url"] == "https://www.google.com/maps/place/?q=place_id:test_place_id"
    assert lead["source_type"] == "google_maps"
    
    # Verify metadata
    assert lead["metadata"]["place_id"] == "test_place_id"
    assert lead["metadata"]["category"] == "Restaurant"
    assert lead["metadata"]["rating"] == 4.5
    assert lead["metadata"]["reviews_count"] == 100
    assert lead["metadata"]["price_level"] == 2


def test_empty_business_data(gmaps_client):
    """Test handling of empty business data."""
    # Test with empty data
    lead = gmaps_client.standardize_to_lead({})
    
    # Should return an empty dictionary
    assert lead == {}
    
    # Test with None
    lead = gmaps_client.standardize_to_lead(None)
    
    # Should return an empty dictionary
    assert lead == {}


@patch('requests.post')
def test_api_endpoint_error(mock_post, gmaps_client):
    """Test handling of API endpoint configuration errors."""
    # Set api_endpoint to None to simulate misconfiguration
    gmaps_client.api_endpoint = None
    
    # Execute query
    result = gmaps_client.execute_query("test_query")
    
    # Should return error message
    assert "error" in result
    assert "API endpoint not configured" in result["error"]
    
    # Verify that no API call was made
    mock_post.assert_not_called() 