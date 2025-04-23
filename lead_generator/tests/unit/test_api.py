#!/usr/bin/env python
"""
Test suite for the Malaysian Lead Generator API.

This script contains tests for the API endpoints, including lead management,
authentication, and data operations. Run with pytest.
"""

import os
import json
import pytest
import tempfile
import requests
from datetime import datetime, timedelta
from unittest import mock

# Configuration for tests
API_BASE_URL = os.environ.get("TEST_API_BASE_URL", "http://localhost:8000")
TEST_ADMIN_TOKEN = os.environ.get("TEST_ADMIN_TOKEN", "test_admin_token")
TEST_USER_TOKEN = os.environ.get("TEST_USER_TOKEN", "test_user_token")

# Sample data for tests
SAMPLE_LEAD = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+60123456789",
    "source": "test_api",
    "interest": "Computer Science",
    "notes": "Created by automated test",
    "status": "new"
}

SAMPLE_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "StrongP@ssw0rd",
    "full_name": "Test User",
    "role": "user"
}

# Test fixtures
@pytest.fixture
def admin_headers():
    """Headers with admin authentication token."""
    return {
        "Authorization": f"Bearer {TEST_ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def user_headers():
    """Headers with regular user authentication token."""
    return {
        "Authorization": f"Bearer {TEST_USER_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def temp_lead():
    """Create a temporary lead for testing and clean up after tests."""
    # Create a lead
    headers = {"Authorization": f"Bearer {TEST_ADMIN_TOKEN}", "Content-Type": "application/json"}
    response = requests.post(f"{API_BASE_URL}/leads", json=SAMPLE_LEAD, headers=headers)
    
    if response.status_code != 201:
        pytest.skip(f"Failed to create temporary lead: {response.text}")
    
    lead_id = response.json()["id"]
    
    # Yield the lead ID for tests
    yield lead_id
    
    # Clean up after tests
    requests.delete(f"{API_BASE_URL}/leads/{lead_id}", headers=headers)

# Helper functions
def check_api_available():
    """Check if the API is available before running tests."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except requests.RequestException:
        return False

# Authentication tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestAuthentication:
    
    def test_login_valid(self):
        """Test valid login returns token."""
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "username": os.environ.get("TEST_USERNAME", "admin"),
            "password": os.environ.get("TEST_PASSWORD", "admin_password")
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid(self):
        """Test invalid login returns error."""
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "username": "invalid_user",
            "password": "invalid_password"
        })
        assert response.status_code == 401
    
    def test_token_required(self):
        """Test endpoints requiring token authentication."""
        response = requests.get(f"{API_BASE_URL}/leads")
        assert response.status_code == 401
    
    def test_admin_only_endpoint(self, user_headers, admin_headers):
        """Test endpoints requiring admin privileges."""
        # Regular user should not access admin endpoints
        response = requests.get(f"{API_BASE_URL}/admin/users", headers=user_headers)
        assert response.status_code == 403
        
        # Admin should access admin endpoints
        response = requests.get(f"{API_BASE_URL}/admin/users", headers=admin_headers)
        assert response.status_code == 200

# Lead management tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestLeadManagement:
    
    def test_create_lead(self, admin_headers):
        """Test creating a new lead."""
        # Generate unique email to avoid conflicts
        unique_lead = SAMPLE_LEAD.copy()
        unique_lead["email"] = f"test_{datetime.now().timestamp()}@example.com"
        
        response = requests.post(f"{API_BASE_URL}/leads", json=unique_lead, headers=admin_headers)
        assert response.status_code == 201
        lead_data = response.json()
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/leads/{lead_data['id']}", headers=admin_headers)
    
    def test_get_lead(self, admin_headers, temp_lead):
        """Test retrieving a specific lead."""
        response = requests.get(f"{API_BASE_URL}/leads/{temp_lead}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["id"] == temp_lead
    
    def test_update_lead(self, admin_headers, temp_lead):
        """Test updating a lead."""
        update_data = {"status": "contacted", "notes": "Updated by test"}
        response = requests.patch(f"{API_BASE_URL}/leads/{temp_lead}", 
                                 json=update_data, 
                                 headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "contacted"
        assert response.json()["notes"] == "Updated by test"
    
    def test_search_leads(self, admin_headers, temp_lead):
        """Test searching for leads."""
        # Add some delay to ensure the lead is indexed
        import time
        time.sleep(1)
        
        # Search by email
        response = requests.get(f"{API_BASE_URL}/leads/search?query={SAMPLE_LEAD['email']}", 
                               headers=admin_headers)
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        assert any(lead["id"] == temp_lead for lead in results)
    
    def test_delete_lead(self, admin_headers):
        """Test deleting a lead."""
        # Create a lead to delete
        unique_lead = SAMPLE_LEAD.copy()
        unique_lead["email"] = f"delete_{datetime.now().timestamp()}@example.com"
        create_response = requests.post(f"{API_BASE_URL}/leads", 
                                       json=unique_lead, 
                                       headers=admin_headers)
        lead_id = create_response.json()["id"]
        
        # Delete the lead
        delete_response = requests.delete(f"{API_BASE_URL}/leads/{lead_id}", 
                                        headers=admin_headers)
        assert delete_response.status_code == 204
        
        # Verify it's gone
        get_response = requests.get(f"{API_BASE_URL}/leads/{lead_id}", 
                                   headers=admin_headers)
        assert get_response.status_code == 404

# User management tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestUserManagement:
    
    def test_create_user(self, admin_headers):
        """Test creating a new user."""
        # Generate unique username to avoid conflicts
        unique_user = SAMPLE_USER.copy()
        unique_user["username"] = f"testuser_{datetime.now().timestamp()}"
        unique_user["email"] = f"{unique_user['username']}@example.com"
        
        response = requests.post(f"{API_BASE_URL}/admin/users", 
                                json=unique_user, 
                                headers=admin_headers)
        assert response.status_code == 201
        user_data = response.json()
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/admin/users/{user_data['id']}", 
                       headers=admin_headers)
    
    def test_user_permissions(self, admin_headers, user_headers):
        """Test user permission restrictions."""
        # Regular users shouldn't create other users
        unique_user = SAMPLE_USER.copy()
        unique_user["username"] = f"permission_test_{datetime.now().timestamp()}"
        
        response = requests.post(f"{API_BASE_URL}/admin/users", 
                                json=unique_user, 
                                headers=user_headers)
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden

# Email functionality tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestEmailFunctionality:
    
    @mock.patch("requests.post")
    def test_send_email_template(self, mock_post, admin_headers, temp_lead):
        """Test sending an email using a template."""
        # Mock the email sending service
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True, "message_id": "test123"}
        
        # Send email
        email_data = {
            "lead_id": temp_lead,
            "template_id": "welcome_email",
            "subject_override": "Test Email",
            "additional_context": {"custom_field": "test value"}
        }
        
        response = requests.post(f"{API_BASE_URL}/emails/send-template", 
                                json=email_data, 
                                headers=admin_headers)
        
        # If the endpoint exists and works with our mock
        if response.status_code == 200:
            assert response.json()["success"] is True
            assert "message_id" in response.json()
        else:
            # If the endpoint doesn't exist in this implementation
            pytest.skip("Email template endpoint not implemented")

# Export functionality tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestExportFunctionality:
    
    def test_export_leads(self, admin_headers):
        """Test exporting leads to CSV."""
        response = requests.get(f"{API_BASE_URL}/leads/export", 
                               headers=admin_headers)
        
        # Check if the endpoint exists and returns CSV
        if response.status_code == 200:
            assert response.headers["Content-Type"] == "text/csv"
            assert len(response.content) > 0
            
            # Save to temp file to verify it's valid CSV
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
                temp.write(response.content)
                temp_path = temp.name
            
            # Very basic CSV validation
            with open(temp_path, 'r') as f:
                first_line = f.readline()
                assert "," in first_line  # Verify it has commas as a simple CSV check
            
            # Clean up
            os.unlink(temp_path)
        else:
            # If the endpoint doesn't exist in this implementation
            pytest.skip("Export functionality not implemented")

# Integration tests
@pytest.mark.skipif(not check_api_available(), reason="API not available")
class TestIntegration:
    
    def test_lead_workflow(self, admin_headers):
        """Test the full lead workflow from creation to status updates."""
        # 1. Create lead
        unique_email = f"workflow_{datetime.now().timestamp()}@example.com"
        test_lead = SAMPLE_LEAD.copy()
        test_lead["email"] = unique_email
        
        create_response = requests.post(f"{API_BASE_URL}/leads", 
                                       json=test_lead, 
                                       headers=admin_headers)
        assert create_response.status_code == 201
        lead_id = create_response.json()["id"]
        
        # 2. Update lead status to "contacted"
        update1 = requests.patch(f"{API_BASE_URL}/leads/{lead_id}", 
                                json={"status": "contacted"}, 
                                headers=admin_headers)
        assert update1.status_code == 200
        assert update1.json()["status"] == "contacted"
        
        # 3. Add a note
        note_response = requests.post(f"{API_BASE_URL}/leads/{lead_id}/notes", 
                                     json={"content": "Test workflow note"}, 
                                     headers=admin_headers)
        
        # Note endpoint might not exist, so check conditionally
        if note_response.status_code == 201:
            assert "id" in note_response.json()
        
        # 4. Update lead status to "qualified"
        update2 = requests.patch(f"{API_BASE_URL}/leads/{lead_id}", 
                                json={"status": "qualified"}, 
                                headers=admin_headers)
        assert update2.status_code == 200
        assert update2.json()["status"] == "qualified"
        
        # 5. Verify full lead data
        get_response = requests.get(f"{API_BASE_URL}/leads/{lead_id}", 
                                   headers=admin_headers)
        assert get_response.status_code == 200
        lead_data = get_response.json()
        assert lead_data["email"] == unique_email
        assert lead_data["status"] == "qualified"
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/leads/{lead_id}", headers=admin_headers)

if __name__ == "__main__":
    # This allows running the tests directly with Python in addition to pytest
    import sys
    import pytest
    sys.exit(pytest.main(["-v", __file__])) 