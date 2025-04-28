"""
Unified data standardization pipeline for MCP-powered API clients.

This module provides functions for standardizing data from different sources
into a common lead format, enriching leads with data from multiple sources,
and deduplicating lead data.
"""

import logging
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

# Set up logging
logger = logging.getLogger(__name__)

# Standard lead schema
STANDARD_LEAD_SCHEMA = {
    "organization": "",            # Business/organization name
    "person_name": "",             # Contact person's name
    "role": "",                    # Contact person's role/title
    "email": "",                   # Primary email address
    "phone": "",                   # Primary phone number
    "address": "",                 # Physical address
    "city": "",                    # City
    "state": "",                   # State/region
    "postal_code": "",             # Postal/zip code
    "country": "Malaysia",         # Country (defaulted to Malaysia)
    "website": "",                 # Website URL
    "industry": "",                # Business industry/category
    "source": "",                  # Data source (e.g., google_maps, instagram, web)
    "social_media": {              # Social media profiles
        "instagram": "",
        "facebook": "",
        "twitter": "",
        "linkedin": ""
    },
    "location": {                  # Geographic coordinates
        "latitude": None,
        "longitude": None
    },
    "rating": None,                # Business rating (if available)
    "reviews_count": 0,            # Number of reviews (if available)
    "timestamp": "",               # When the lead was collected
    "metadata": {}                 # Source-specific additional data
}

def standardize_lead(source_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
    """
    Standardize source-specific data to the common lead format.
    
    Args:
        source_data: Data from a specific source (Google Maps, Instagram, etc.)
        source_type: Type of the source (google_maps, instagram, web_browser)
        
    Returns:
        Standardized lead data dictionary
    """
    # Start with the standard schema
    lead = STANDARD_LEAD_SCHEMA.copy()
    
    # Set the source and timestamp
    lead["source"] = source_type
    lead["timestamp"] = datetime.now().isoformat()
    
    # Apply source-specific mapping
    if source_type == "google_maps":
        return _map_google_maps_data(source_data, lead)
    elif source_type == "instagram":
        return _map_instagram_data(source_data, lead)
    elif source_type == "web_browser":
        return _map_web_browser_data(source_data, lead)
    else:
        logger.warning(f"Unknown source type: {source_type}")
        return lead

def _map_google_maps_data(source_data: Dict[str, Any], lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Google Maps data to the standard lead format.
    
    Args:
        source_data: Google Maps data
        lead: Base lead dictionary
        
    Returns:
        Mapped lead data
    """
    # Extract basic information
    lead["organization"] = source_data.get("name", "")
    lead["phone"] = source_data.get("phone", "")
    lead["website"] = source_data.get("website", "")
    
    # Handle address
    if "address" in source_data:
        address_parts = _parse_address(source_data["address"])
        lead["address"] = address_parts.get("street", "")
        lead["city"] = address_parts.get("city", "")
        lead["state"] = address_parts.get("state", "")
        lead["postal_code"] = address_parts.get("postal_code", "")
    
    # Handle coordinates
    if "coordinates" in source_data:
        lead["location"]["latitude"] = source_data["coordinates"].get("latitude")
        lead["location"]["longitude"] = source_data["coordinates"].get("longitude")
    
    # Handle ratings and reviews
    lead["rating"] = source_data.get("rating")
    lead["reviews_count"] = source_data.get("reviews", 0)
    
    # Handle categories/industry
    if "category" in source_data:
        categories = source_data["category"].split(",")
        lead["industry"] = categories[0].strip() if categories else ""
    
    # Store original data in metadata
    lead["metadata"]["google_maps"] = source_data
    
    return lead

def _map_instagram_data(source_data: Dict[str, Any], lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Instagram data to the standard lead format.
    
    Args:
        source_data: Instagram data
        lead: Base lead dictionary
        
    Returns:
        Mapped lead data
    """
    # Handle profile data
    if source_data.get("username"):
        # This is profile data
        lead["organization"] = source_data.get("full_name", "")
        lead["email"] = source_data.get("email", "")
        lead["phone"] = source_data.get("phone", "")
        lead["website"] = source_data.get("website", "")
        lead["industry"] = source_data.get("business_category", "")
        
        # Social media
        lead["social_media"]["instagram"] = f"https://www.instagram.com/{source_data.get('username', '')}"
        
        # Location data if available
        if "address" in source_data:
            lead["address"] = source_data["address"]
        if "city" in source_data:
            lead["city"] = source_data["city"]
        if "zip_code" in source_data:
            lead["postal_code"] = source_data["zip_code"]
    
    # Store original data in metadata
    lead["metadata"]["instagram"] = source_data
    
    return lead

def _map_web_browser_data(source_data: Dict[str, Any], lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Web Browser data to the standard lead format.
    
    Args:
        source_data: Web Browser data
        lead: Base lead dictionary
        
    Returns:
        Mapped lead data
    """
    # Extract from content if available
    content = ""
    if "content" in source_data:
        content = source_data["content"]
    elif "title" in source_data:
        content = source_data["title"]
    
    # Extract organization name from title
    if "title" in source_data:
        title = source_data["title"]
        lead["organization"] = title.split(" | ")[0].strip()
    
    # Extract contact information from content
    contact_info = _extract_contact_info(content)
    lead["email"] = contact_info.get("email", "")
    lead["phone"] = contact_info.get("phone", "")
    lead["address"] = contact_info.get("address", "")
    lead["website"] = source_data.get("url", "")
    
    # Store original data in metadata
    lead["metadata"]["web_browser"] = source_data
    
    return lead

def enrich_lead(primary_lead: Dict[str, Any], additional_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enrich a primary lead with data from additional leads.
    
    Args:
        primary_lead: The primary lead to enrich
        additional_leads: Additional leads with supplementary data
        
    Returns:
        Enriched lead data
    """
    enriched_lead = primary_lead.copy()
    
    # Track fields that have been filled
    for additional_lead in additional_leads:
        # Fill missing basic information
        for field in ["email", "phone", "website", "person_name", "role", "industry"]:
            if not enriched_lead.get(field) and additional_lead.get(field):
                enriched_lead[field] = additional_lead[field]
                logger.debug(f"Enriched lead with {field} from {additional_lead['source']}")
        
        # Fill missing address information
        for field in ["address", "city", "state", "postal_code"]:
            if not enriched_lead.get(field) and additional_lead.get(field):
                enriched_lead[field] = additional_lead[field]
                logger.debug(f"Enriched lead with {field} from {additional_lead['source']}")
        
        # Add social media profiles
        for platform, url in additional_lead.get("social_media", {}).items():
            if url and not enriched_lead["social_media"].get(platform):
                enriched_lead["social_media"][platform] = url
                logger.debug(f"Enriched lead with {platform} from {additional_lead['source']}")
        
        # Merge metadata
        source = additional_lead.get("source")
        if source and source not in enriched_lead["metadata"]:
            enriched_lead["metadata"][source] = additional_lead.get("metadata", {}).get(source, {})
    
    # Calculate completeness score
    enriched_lead["completeness_score"] = _calculate_completeness_score(enriched_lead)
    
    return enriched_lead

def deduplicate_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate leads based on organization name, phone, email, and website.
    
    Args:
        leads: List of lead dictionaries
        
    Returns:
        Deduplicated list of leads
    """
    if not leads:
        return []
    
    unique_leads = []
    seen_organizations = set()
    seen_emails = set()
    seen_phones = set()
    seen_websites = set()
    
    # First pass: Group leads by organization
    org_groups = {}
    for lead in leads:
        org_name = _normalize_org_name(lead.get("organization", ""))
        if org_name:
            if org_name not in org_groups:
                org_groups[org_name] = []
            org_groups[org_name].append(lead)
    
    # Second pass: For each organization group, merge and add unique leads
    for org_name, org_leads in org_groups.items():
        if not org_leads:
            continue
        
        # Use the lead with the highest completeness as primary
        org_leads.sort(key=_calculate_completeness_score, reverse=True)
        primary_lead = org_leads[0]
        additional_leads = org_leads[1:]
        
        # Enrich the primary lead with data from additional leads
        if additional_leads:
            enriched_lead = enrich_lead(primary_lead, additional_leads)
        else:
            enriched_lead = primary_lead
        
        # Check if we've seen this lead before
        org_id = _normalize_org_name(enriched_lead.get("organization", ""))
        email = enriched_lead.get("email", "").lower()
        phone = _normalize_phone(enriched_lead.get("phone", ""))
        website = _normalize_website(enriched_lead.get("website", ""))
        
        # Skip if we've seen all identifiers
        if (org_id and org_id in seen_organizations and 
            ((email and email in seen_emails) or 
             (phone and phone in seen_phones) or 
             (website and website in seen_websites))):
            continue
        
        # Add to unique leads and track identifiers
        unique_leads.append(enriched_lead)
        if org_id:
            seen_organizations.add(org_id)
        if email:
            seen_emails.add(email)
        if phone:
            seen_phones.add(phone)
        if website:
            seen_websites.add(website)
    
    logger.info(f"Deduplicated {len(leads)} leads into {len(unique_leads)} unique leads")
    return unique_leads

def _parse_address(address: str) -> Dict[str, str]:
    """
    Parse an address string into components.
    
    Args:
        address: Full address string
        
    Returns:
        Dictionary of address components
    """
    components = {
        "street": "",
        "city": "",
        "state": "",
        "postal_code": ""
    }
    
    # Malaysian postal code pattern
    postal_code_pattern = r'\b\d{5}\b'
    postal_code_match = re.search(postal_code_pattern, address)
    
    if postal_code_match:
        components["postal_code"] = postal_code_match.group(0)
    
    # Common Malaysian states
    states = [
        "Johor", "Kedah", "Kelantan", "Kuala Lumpur", "Labuan", "Melaka", "Negeri Sembilan",
        "Pahang", "Penang", "Perak", "Perlis", "Putrajaya", "Sabah", "Sarawak", "Selangor", "Terengganu"
    ]
    
    for state in states:
        if state in address:
            components["state"] = state
            # Try to extract city
            parts = address.split(state)
            if len(parts) > 1:
                city_part = parts[0].strip().split(",")
                if city_part:
                    components["city"] = city_part[-1].strip()
            break
    
    # If we didn't find a state but have multiple commas, extract city
    if not components["city"] and "," in address:
        parts = address.split(",")
        if len(parts) >= 2:
            components["city"] = parts[-2].strip()
    
    # Street is everything before the city or first comma if no city
    if components["city"] and components["city"] in address:
        street_part = address.split(components["city"])[0]
        components["street"] = street_part.strip().rstrip(",")
    elif "," in address:
        components["street"] = address.split(",")[0].strip()
    else:
        components["street"] = address
    
    return components

def _extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extract contact information from text.
    
    Args:
        text: Text to extract contact info from
        
    Returns:
        Dictionary with email, phone, and address
    """
    contact_info = {
        "email": "",
        "phone": "",
        "address": ""
    }
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info["email"] = emails[0]  # Use the first found email
    
    # Extract Malaysian phone numbers
    # Patterns: +60xxxxxxxxx, 01x-xxxxxxx, 01x xxxxxxx, etc.
    phone_patterns = [
        r'(?:\+60|0060|60)(?:\d[ -]?){8,10}',  # +60 format
        r'0\d(?:\d[ -]?){7,9}'                 # 01x format
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            # Clean up the phone number
            phone = phones[0]
            phone = re.sub(r'[ -]', '', phone)  # Remove spaces and dashes
            contact_info["phone"] = phone
            break
    
    return contact_info

def _normalize_org_name(name: str) -> str:
    """
    Normalize organization name for comparison.
    
    Args:
        name: Organization name
        
    Returns:
        Normalized name
    """
    if not name:
        return ""
    
    # Remove common terms, lowercase, and remove non-alphanumeric chars
    common_terms = ["sdn bhd", "bhd", "berhad", "enterprise", "company", "inc", "llc", "ltd", "limited"]
    normalized = name.lower()
    
    for term in common_terms:
        normalized = normalized.replace(term, "")
    
    # Remove non-alphanumeric characters and extra spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def _normalize_phone(phone: str) -> str:
    """
    Normalize phone number for comparison.
    
    Args:
        phone: Phone number
        
    Returns:
        Normalized phone number
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    normalized = re.sub(r'\D', '', phone)
    
    # Ensure Malaysian format
    if normalized.startswith("60"):
        return normalized
    elif normalized.startswith("0"):
        return "60" + normalized[1:]
    else:
        return normalized

def _normalize_website(url: str) -> str:
    """
    Normalize website URL for comparison.
    
    Args:
        url: Website URL
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Remove protocol, www, and trailing slashes
    normalized = url.lower()
    normalized = re.sub(r'^https?://', '', normalized)
    normalized = re.sub(r'^www\.', '', normalized)
    normalized = normalized.rstrip('/')
    
    return normalized

def _calculate_completeness_score(lead: Dict[str, Any]) -> float:
    """
    Calculate a completeness score for a lead.
    
    Args:
        lead: Lead data
        
    Returns:
        Completeness score between 0 and 1
    """
    # Define weights for different fields
    weights = {
        "organization": 1.0,
        "person_name": 0.7,
        "role": 0.5,
        "email": 1.0,
        "phone": 1.0,
        "address": 0.8,
        "city": 0.6,
        "state": 0.4,
        "postal_code": 0.3,
        "website": 0.9,
        "industry": 0.7,
        "social_media": 0.6,
        "location": 0.5
    }
    
    # Calculate weighted score
    total_weight = sum(weights.values())
    score = 0.0
    
    for field, weight in weights.items():
        if field == "social_media":
            # Check if any social media links exist
            if any(lead.get("social_media", {}).values()):
                score += weight
        elif field == "location":
            # Check if location coordinates exist
            if lead.get("location", {}).get("latitude") and lead.get("location", {}).get("longitude"):
                score += weight
        elif lead.get(field):
            score += weight
    
    return score / total_weight

def filter_leads_by_completeness(leads: List[Dict[str, Any]], min_score: float = 0.5) -> List[Dict[str, Any]]:
    """
    Filter leads by completeness score.
    
    Args:
        leads: List of lead dictionaries
        min_score: Minimum completeness score (0-1)
        
    Returns:
        Filtered list of leads
    """
    if not leads:
        return []
    
    # Calculate completeness score for each lead
    for lead in leads:
        if "completeness_score" not in lead:
            lead["completeness_score"] = _calculate_completeness_score(lead)
    
    # Filter leads by score
    filtered_leads = [lead for lead in leads if lead.get("completeness_score", 0) >= min_score]
    
    logger.info(f"Filtered {len(leads)} leads to {len(filtered_leads)} leads with min score {min_score}")
    return filtered_leads

def batch_standardize(data_sources: List[Tuple[Dict[str, Any], str]]) -> List[Dict[str, Any]]:
    """
    Standardize multiple data sources in batch.
    
    Args:
        data_sources: List of (source_data, source_type) tuples
        
    Returns:
        List of standardized leads
    """
    standardized_leads = []
    
    for source_data, source_type in data_sources:
        try:
            lead = standardize_lead(source_data, source_type)
            standardized_leads.append(lead)
        except Exception as e:
            logger.error(f"Error standardizing {source_type} data: {e}")
    
    return standardized_leads

def get_lead_statistics(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about a collection of leads.
    
    Args:
        leads: List of lead dictionaries
        
    Returns:
        Statistics dictionary
    """
    if not leads:
        return {
            "total_leads": 0,
            "sources": {},
            "completeness": {
                "average_score": 0,
                "fields": {}
            }
        }
    
    total_leads = len(leads)
    
    # Count leads by source
    sources = {}
    for lead in leads:
        source = lead.get("source", "unknown")
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    # Calculate field completeness
    fields = ["organization", "person_name", "role", "email", "phone", 
              "address", "city", "state", "postal_code", "website", "industry"]
    
    field_completeness = {}
    for field in fields:
        count = sum(1 for lead in leads if lead.get(field))
        field_completeness[field] = {
            "count": count,
            "percentage": round(count / total_leads * 100, 1)
        }
    
    # Calculate average completeness score
    avg_score = sum(lead.get("completeness_score", _calculate_completeness_score(lead)) for lead in leads) / total_leads
    
    return {
        "total_leads": total_leads,
        "sources": sources,
        "completeness": {
            "average_score": round(avg_score, 2),
            "fields": field_completeness
        }
    } 