"""
Targeting Strategy Configuration.

This module defines targeting strategies based on business categories
to optimize lead generation and conversion rates.
"""

from typing import Dict, List, Any, Optional

# Define targeting tiers and priorities
TARGETING_TIERS = {
    "high_priority": {
        "description": "High priority businesses that match our ideal client profile",
        "template": "exec_tone",
        "proposal": "premium",
        "min_score": 0.7,
        "follow_up_days": 3
    },
    "medium_priority": {
        "description": "Medium priority businesses that match some aspects of our ideal client profile",
        "template": "default",
        "proposal": "standard",
        "min_score": 0.5,
        "follow_up_days": 5
    },
    "low_priority": {
        "description": "Low priority businesses that might benefit from our services",
        "template": "default",
        "proposal": "basic",
        "min_score": 0.3,
        "follow_up_days": 7
    }
}

# Map business categories to targeting tiers
CATEGORY_TARGETING = {
    # Technology sector
    "software development": "high_priority",
    "app development": "high_priority",
    "web development": "high_priority",
    "digital agency": "high_priority",
    "it services": "high_priority",
    "information technology": "high_priority",
    "technology": "high_priority",
    "tech startup": "high_priority",
    "digital marketing": "high_priority",
    "artificial intelligence": "high_priority",
    "data analytics": "high_priority",
    
    # Business services
    "business consulting": "high_priority",
    "management consulting": "high_priority",
    "marketing agency": "medium_priority",
    "advertising agency": "medium_priority",
    "financial services": "medium_priority",
    "accounting": "medium_priority",
    "legal services": "medium_priority",
    "recruitment": "medium_priority",
    "human resources": "medium_priority",
    
    # Education
    "education": "medium_priority",
    "training center": "medium_priority",
    "university": "medium_priority",
    "college": "medium_priority",
    "school": "low_priority",
    "tutoring": "low_priority",
    "language center": "low_priority",
    
    # Events & Hospitality
    "event management": "medium_priority",
    "event planner": "medium_priority",
    "hotel": "low_priority",
    "resort": "low_priority",
    "restaurant": "low_priority",
    "catering": "low_priority",
    
    # Retail & Commerce
    "e-commerce": "medium_priority",
    "retail": "low_priority",
    "wholesale": "low_priority",
    "shopping mall": "low_priority",
    
    # Manufacturing & Engineering
    "manufacturing": "medium_priority",
    "engineering": "medium_priority",
    "construction": "medium_priority",
    "architecture": "medium_priority",
    
    # Health & Wellness
    "healthcare": "low_priority",
    "medical": "low_priority",
    "fitness": "low_priority",
    "spa": "low_priority",
    "wellness": "low_priority",
    
    # Default for unrecognized categories
    "default": "low_priority"
}

# Location-based adjustments
LOCATION_PRIORITY_BOOST = {
    "Kuala Lumpur": 1,
    "Petaling Jaya": 1,
    "Cyberjaya": 1,
    "Shah Alam": 0.5,
    "Penang": 0.5,
    "Johor Bahru": 0.5,
    "Selangor": 0.5
}

def get_targeting_tier(lead: Dict[str, Any]) -> str:
    """
    Determine the targeting tier for a lead based on business category.
    
    Args:
        lead: The lead data dictionary
        
    Returns:
        The targeting tier (high_priority, medium_priority, or low_priority)
    """
    # Extract industry/category from the lead
    industry = lead.get("industry", "").lower() if lead.get("industry") else ""
    
    # Find matching category
    matching_tier = CATEGORY_TARGETING.get("default", "low_priority")
    
    for category, tier in CATEGORY_TARGETING.items():
        if category in industry:
            matching_tier = tier
            break
    
    # Apply location-based adjustments
    city = lead.get("city", "").strip() if lead.get("city") else ""
    state = lead.get("state", "").strip() if lead.get("state") else ""
    
    # Try to match location for priority boost
    location_boost = 0
    for location, boost in LOCATION_PRIORITY_BOOST.items():
        if location.lower() in city.lower() or location.lower() in state.lower():
            location_boost = boost
            break
    
    # Apply boost if needed
    if location_boost > 0:
        if matching_tier == "medium_priority" and location_boost >= 1:
            matching_tier = "high_priority"
        elif matching_tier == "low_priority" and location_boost >= 0.5:
            matching_tier = "medium_priority"
    
    return matching_tier

def get_targeting_strategy(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the complete targeting strategy for a lead.
    
    Args:
        lead: The lead data dictionary
        
    Returns:
        Dictionary with targeting strategy details
    """
    # Get the targeting tier
    tier = get_targeting_tier(lead)
    
    # Get strategy details
    strategy = TARGETING_TIERS.get(tier, TARGETING_TIERS["low_priority"]).copy()
    
    # Add tier to the strategy
    strategy["tier"] = tier
    
    # Add category insights
    industry = lead.get("industry", "").lower() if lead.get("industry") else ""
    
    if "software" in industry or "technology" in industry or "digital" in industry:
        strategy["industry_insights"] = "Technology sector businesses need solutions that enhance efficiency, scale with growth, and maintain security."
    elif "consulting" in industry or "management" in industry:
        strategy["industry_insights"] = "Consulting firms benefit from tools that improve client management, reporting capabilities, and presentation quality."
    elif "marketing" in industry or "advertising" in industry:
        strategy["industry_insights"] = "Marketing agencies seek solutions that streamline campaign management, analytics reporting, and creative processes."
    elif "education" in industry or "training" in industry:
        strategy["industry_insights"] = "Educational organizations value tools that enhance learning experiences, administrative efficiency, and student engagement."
    elif "event" in industry:
        strategy["industry_insights"] = "Event management companies require solutions for scheduling, logistics coordination, and attendee management."
    else:
        strategy["industry_insights"] = "Businesses in this industry typically benefit from improved operational efficiency and customer engagement tools."
    
    return strategy 