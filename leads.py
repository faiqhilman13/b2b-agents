"""Lead management module.

This module handles lead data operations for the Lead Generator API.
"""

import csv
import json
import logging
import os
from typing import Any, Dict, List, Optional
import math

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define path to leads data
LEADS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "leads.json"
)

def get_all_leads() -> List[Dict[str, Any]]:
    """Get all leads from the data file.
    
    Returns:
        List of leads
    
    Raises:
        FileNotFoundError: If the leads file does not exist
        json.JSONDecodeError: If the leads file is not valid JSON
    """
    try:
        if not os.path.exists(LEADS_FILE):
            logger.warning(f"Leads file {LEADS_FILE} does not exist, returning empty list")
            return []
        
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            leads = json.load(f)
            
        logger.info(f"Retrieved {len(leads)} leads from {LEADS_FILE}")
        return leads
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing leads file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting leads: {str(e)}")
        raise

def filter_leads(
    leads: List[Dict[str, Any]],
    source: Optional[str] = None,
    organization: Optional[str] = None,
    has_email: Optional[bool] = None,
    has_phone: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """Filter leads based on criteria.
    
    Args:
        leads: List of leads to filter
        source: Filter by source
        organization: Filter by organization
        has_email: Filter by email presence
        has_phone: Filter by phone presence
        
    Returns:
        Filtered list of leads
    """
    filtered_leads = leads.copy()
    
    # Apply filters
    if source:
        filtered_leads = [lead for lead in filtered_leads if lead.get('source') == source]
        
    if organization:
        filtered_leads = [lead for lead in filtered_leads if lead.get('organization') == organization]
        
    if has_email is not None:
        if has_email:
            filtered_leads = [lead for lead in filtered_leads if lead.get('email')]
        else:
            filtered_leads = [lead for lead in filtered_leads if not lead.get('email')]
            
    if has_phone is not None:
        if has_phone:
            filtered_leads = [lead for lead in filtered_leads if lead.get('phone')]
        else:
            filtered_leads = [lead for lead in filtered_leads if not lead.get('phone')]
    
    logger.info(f"Filtered to {len(filtered_leads)} leads")
    return filtered_leads

def paginate_leads(
    leads: List[Dict[str, Any]],
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """Paginate leads.
    
    Args:
        leads: List of leads to paginate
        page: Page number
        per_page: Items per page
        
    Returns:
        Paginated result
    """
    # Ensure valid pagination parameters
    page = max(1, page)
    per_page = max(1, min(100, per_page))  # Limit max per_page to 100
    
    # Calculate pagination
    total = len(leads)
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    # Ensure valid page number
    page = min(page, pages)
    
    # Get items for the current page
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total)
    items = leads[start_idx:end_idx]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "per_page": per_page
    }

def get_lead_statistics(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about leads.
    
    Args:
        leads: List of leads
        
    Returns:
        Lead statistics
    """
    total_leads = len(leads)
    
    # Count leads with email and phone
    leads_with_email = sum(1 for lead in leads if lead.get('email'))
    leads_with_phone = sum(1 for lead in leads if lead.get('phone'))
    leads_with_both = sum(1 for lead in leads if lead.get('email') and lead.get('phone'))
    
    # Count by source
    sources = {}
    for lead in leads:
        source = lead.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    # Calculate data completeness
    fields = ['name', 'organization', 'email', 'phone', 'role']
    data_completeness = {}
    
    for field in fields:
        completeness = sum(1 for lead in leads if lead.get(field)) / total_leads if total_leads > 0 else 0
        data_completeness[field] = round(completeness * 100, 2)
    
    return {
        "total_leads": total_leads,
        "leads_with_email": leads_with_email,
        "leads_with_phone": leads_with_phone,
        "leads_with_both": leads_with_both,
        "sources": sources,
        "data_completeness": data_completeness
    }

def export_leads_to_csv(leads: List[Dict[str, Any]], output_file: str) -> Dict[str, Any]:
    """Export leads to CSV file.
    
    Args:
        leads: List of leads
        output_file: Output file path
        
    Returns:
        Result of the export operation
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Define fieldnames for CSV
        fieldnames = ['name', 'organization', 'email', 'phone', 'role', 'source', 'notes']
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write each lead, filtering out None values
            for lead in leads:
                # Only include fields that are in fieldnames
                cleaned_lead = {k: v for k, v in lead.items() if k in fieldnames and v is not None}
                writer.writerow(cleaned_lead)
        
        return {
            "success": True,
            "count": len(leads),
            "file": output_file
        }
    except Exception as e:
        logger.error(f"Error exporting leads to CSV: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def save_leads(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save leads to the data file.
    
    Args:
        leads: List of leads
        
    Returns:
        Result of the save operation
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(LEADS_FILE), exist_ok=True)
        
        # Write to JSON
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "count": len(leads),
            "file": LEADS_FILE
        }
    except Exception as e:
        logger.error(f"Error saving leads: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 