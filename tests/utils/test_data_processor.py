"""
Tests for the unified data standardization pipeline.
"""

import pytest
from datetime import datetime
from lead_generator.utils.data_processor import (
    standardize_lead,
    enrich_lead,
    deduplicate_leads,
    _parse_address,
    _extract_contact_info,
    _normalize_org_name,
    _normalize_phone,
    _normalize_website,
    _calculate_completeness_score,
    filter_leads_by_completeness,
    batch_standardize,
    get_lead_statistics
)

# Test data
GOOGLE_MAPS_DATA = {
    "name": "Tech Solutions Sdn Bhd",
    "place_id": "ChIJ123456789abcdef",
    "address": "123 Jalan Bukit Bintang, Kuala Lumpur 50200, Malaysia",
    "phone": "+60312345678",
    "website": "https://www.techsolutions.my",
    "rating": 4.5,
    "reviews": 100,
    "category": "Software Development, IT Services",
    "coordinates": {
        "latitude": 3.1478,
        "longitude": 101.7152
    }
}

INSTAGRAM_DATA = {
    "username": "techsolutionsmy",
    "full_name": "Tech Solutions Malaysia",
    "biography": "Leading software development company in Malaysia. Contact: info@techsolutions.my",
    "email": "info@techsolutions.my",
    "phone": "+60387654321",
    "website": "http://techsolutions.my",
    "business_category": "Technology / Software",
    "city": "Kuala Lumpur"
}

WEB_BROWSER_DATA = {
    "url": "https://www.techsolutions.my",
    "title": "Tech Solutions | Professional Software Development",
    "content": "Tech Solutions is a leading software development company based in Kuala Lumpur. Contact us at sales@techsolutions.my or call our office at +60378901234. Visit us at 123 Jalan Bukit Bintang, Kuala Lumpur."
}


class TestDataStandardization:
    """Test cases for lead data standardization."""
    
    def test_standardize_google_maps_data(self):
        """Test standardization of Google Maps data."""
        lead = standardize_lead(GOOGLE_MAPS_DATA, "google_maps")
        
        assert lead["organization"] == "Tech Solutions Sdn Bhd"
        assert lead["phone"] == "+60312345678"
        assert lead["website"] == "https://www.techsolutions.my"
        assert lead["industry"] == "Software Development"
        assert lead["location"]["latitude"] == 3.1478
        assert lead["location"]["longitude"] == 101.7152
        assert lead["rating"] == 4.5
        assert lead["reviews_count"] == 100
        assert lead["source"] == "google_maps"
        assert lead["metadata"]["google_maps"] == GOOGLE_MAPS_DATA
        
        # Check address parsing
        assert "Jalan Bukit Bintang" in lead["address"]
        assert lead["city"] == "Kuala Lumpur"
        assert lead["postal_code"] == "50200"
        
    def test_standardize_instagram_data(self):
        """Test standardization of Instagram data."""
        lead = standardize_lead(INSTAGRAM_DATA, "instagram")
        
        assert lead["organization"] == "Tech Solutions Malaysia"
        assert lead["email"] == "info@techsolutions.my"
        assert lead["phone"] == "+60387654321"
        assert lead["website"] == "http://techsolutions.my"
        assert lead["industry"] == "Technology / Software"
        assert lead["city"] == "Kuala Lumpur"
        assert lead["social_media"]["instagram"] == "https://www.instagram.com/techsolutionsmy"
        assert lead["source"] == "instagram"
        assert lead["metadata"]["instagram"] == INSTAGRAM_DATA
        
    def test_standardize_web_browser_data(self):
        """Test standardization of Web Browser data."""
        lead = standardize_lead(WEB_BROWSER_DATA, "web_browser")
        
        assert lead["organization"] == "Tech Solutions"
        assert "sales@techsolutions.my" in lead["email"]
        assert "+60378901234" in lead["phone"]
        assert lead["website"] == "https://www.techsolutions.my"
        assert lead["source"] == "web_browser"
        assert lead["metadata"]["web_browser"] == WEB_BROWSER_DATA
        
    def test_enrichment(self):
        """Test lead enrichment from multiple sources."""
        # Create leads from different sources
        google_lead = standardize_lead(GOOGLE_MAPS_DATA, "google_maps")
        instagram_lead = standardize_lead(INSTAGRAM_DATA, "instagram")
        web_lead = standardize_lead(WEB_BROWSER_DATA, "web_browser")
        
        # Enrich the Google Maps lead with data from Instagram and web
        enriched_lead = enrich_lead(google_lead, [instagram_lead, web_lead])
        
        # Check that enrichment worked correctly
        assert enriched_lead["organization"] == "Tech Solutions Sdn Bhd"  # Kept from primary
        assert enriched_lead["email"] == "info@techsolutions.my"  # Added from Instagram
        assert enriched_lead["phone"] == "+60312345678"  # Kept from primary
        assert enriched_lead["website"] == "https://www.techsolutions.my"  # Kept from primary
        assert enriched_lead["social_media"]["instagram"] == "https://www.instagram.com/techsolutionsmy"
        assert "completeness_score" in enriched_lead
        assert "instagram" in enriched_lead["metadata"]
        assert "google_maps" in enriched_lead["metadata"]
        
    def test_deduplication(self):
        """Test lead deduplication."""
        # Create several leads with overlapping information
        leads = [
            {
                "organization": "Tech Solutions Sdn Bhd",
                "email": "info@techsolutions.my",
                "phone": "+60312345678",
                "source": "google_maps"
            },
            {
                "organization": "Tech Solutions Malaysia",
                "email": "info@techsolutions.my",
                "website": "https://www.techsolutions.my",
                "source": "instagram"
            },
            {
                "organization": "Tech Solutions",
                "phone": "+60312345678",
                "address": "123 Jalan Bukit Bintang",
                "source": "web_browser"
            },
            {
                "organization": "Different Company",
                "email": "contact@different.com",
                "phone": "+60399998888",
                "source": "google_maps"
            }
        ]
        
        # Deduplicate the leads
        unique_leads = deduplicate_leads(leads)
        
        # Should have 2 unique companies
        assert len(unique_leads) == 2
        
        # The Tech Solutions leads should be merged
        tech_lead = next((l for l in unique_leads if "Tech Solutions" in l["organization"]), None)
        assert tech_lead is not None
        assert tech_lead["email"] == "info@techsolutions.my"
        assert tech_lead["phone"] == "+60312345678"
        assert tech_lead["website"] == "https://www.techsolutions.my"
        assert tech_lead["address"] == "123 Jalan Bukit Bintang"
        
        # The Different Company lead should be preserved
        diff_lead = next((l for l in unique_leads if "Different Company" in l["organization"]), None)
        assert diff_lead is not None
        assert diff_lead["email"] == "contact@different.com"
        
    def test_address_parsing(self):
        """Test address parsing function."""
        # Test a complete Malaysian address
        address = "123 Jalan Bukit Bintang, Bukit Bintang, Kuala Lumpur 50200, Malaysia"
        components = _parse_address(address)
        
        assert components["street"] == "123 Jalan Bukit Bintang"
        assert components["city"] == "Bukit Bintang"
        assert components["state"] == "Kuala Lumpur"
        assert components["postal_code"] == "50200"
        
        # Test a simple address
        address = "15 Jalan PJU, Petaling Jaya 47810"
        components = _parse_address(address)
        
        assert components["street"] == "15 Jalan PJU"
        assert components["city"] == "Petaling Jaya"
        assert components["postal_code"] == "47810"
        
    def test_contact_info_extraction(self):
        """Test contact information extraction."""
        # Test extracting from text with email and phone
        text = "Contact us at info@example.com or call +60123456789 for more information."
        contact_info = _extract_contact_info(text)
        
        assert contact_info["email"] == "info@example.com"
        assert contact_info["phone"] == "+60123456789"
        
        # Test Malaysian phone number formats
        text = "Call our hotline 011-23456789 or 03-12345678"
        contact_info = _extract_contact_info(text)
        
        assert "01123456789" in contact_info["phone"] or "0312345678" in contact_info["phone"]
        
    def test_name_normalization(self):
        """Test organization name normalization."""
        assert _normalize_org_name("Tech Solutions Sdn Bhd") == "tech solutions"
        assert _normalize_org_name("TECH SOLUTIONS SDN. BHD.") == "tech solutions"
        assert _normalize_org_name("Tech-Solutions (M) Bhd") == "techsolutions m"
        
    def test_phone_normalization(self):
        """Test phone number normalization."""
        assert _normalize_phone("+60123456789") == "60123456789"
        assert _normalize_phone("0123456789") == "60123456789"
        assert _normalize_phone("012-345-6789") == "60123456789"
        
    def test_website_normalization(self):
        """Test website URL normalization."""
        assert _normalize_website("https://www.example.com/") == "example.com"
        assert _normalize_website("http://example.com") == "example.com"
        assert _normalize_website("www.example.com/index.html") == "example.com/index.html"
        
    def test_completeness_scoring(self):
        """Test lead completeness scoring."""
        # Test a complete lead
        complete_lead = {
            "organization": "Complete Company",
            "person_name": "John Smith",
            "role": "CEO",
            "email": "john@complete.com",
            "phone": "+60123456789",
            "address": "123 Main Street",
            "city": "Kuala Lumpur",
            "state": "Kuala Lumpur",
            "postal_code": "50000",
            "website": "https://www.complete.com",
            "industry": "Technology",
            "social_media": {"instagram": "https://instagram.com/complete"}
        }
        
        complete_score = _calculate_completeness_score(complete_lead)
        assert complete_score > 0.9  # Should be very high
        
        # Test a partial lead
        partial_lead = {
            "organization": "Partial Company",
            "email": "info@partial.com",
            "website": "https://www.partial.com"
        }
        
        partial_score = _calculate_completeness_score(partial_lead)
        assert 0.2 < partial_score < 0.5  # Should be medium-low
        
    def test_filtering_by_completeness(self):
        """Test filtering leads by completeness score."""
        leads = [
            {
                "organization": "Complete Company",
                "email": "info@complete.com",
                "phone": "+60123456789",
                "address": "123 Main Street",
                "website": "https://www.complete.com",
                "industry": "Technology"
            },
            {
                "organization": "Partial Company",
                "email": "info@partial.com"
            },
            {
                "organization": "Minimal Company"
            }
        ]
        
        # Filter with default threshold (0.5)
        filtered = filter_leads_by_completeness(leads)
        assert len(filtered) == 1
        assert filtered[0]["organization"] == "Complete Company"
        
        # Filter with lower threshold
        filtered = filter_leads_by_completeness(leads, min_score=0.2)
        assert len(filtered) == 2
        
    def test_batch_standardization(self):
        """Test batch standardization of multiple sources."""
        data_sources = [
            (GOOGLE_MAPS_DATA, "google_maps"),
            (INSTAGRAM_DATA, "instagram"),
            (WEB_BROWSER_DATA, "web_browser")
        ]
        
        leads = batch_standardize(data_sources)
        assert len(leads) == 3
        
        # Check that each source was standardized correctly
        sources = [lead["source"] for lead in leads]
        assert "google_maps" in sources
        assert "instagram" in sources
        assert "web_browser" in sources
        
    def test_lead_statistics(self):
        """Test generating lead statistics."""
        leads = [
            {
                "organization": "Company A",
                "email": "info@companya.com",
                "phone": "+60123456789",
                "source": "google_maps"
            },
            {
                "organization": "Company B",
                "website": "https://www.companyb.com",
                "source": "instagram"
            },
            {
                "organization": "Company C",
                "email": "info@companyc.com",
                "source": "google_maps"
            }
        ]
        
        stats = get_lead_statistics(leads)
        
        assert stats["total_leads"] == 3
        assert stats["sources"]["google_maps"] == 2
        assert stats["sources"]["instagram"] == 1
        assert stats["completeness"]["fields"]["email"]["count"] == 2
        assert stats["completeness"]["fields"]["phone"]["count"] == 1
        assert stats["completeness"]["average_score"] > 0 