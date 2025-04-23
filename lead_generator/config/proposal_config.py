#!/usr/bin/env python3
"""
Proposal Configuration for Package-Based PDF Selection.

This module defines configuration for attaching different PDF packages
to outreach emails based on lead characteristics and organization type.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Base directory for proposal PDFs
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROPOSALS_DIR = BASE_DIR / "proposals"

# Ensure proposals directory exists
os.makedirs(PROPOSALS_DIR, exist_ok=True)

# Define the package types and their PDF files
PACKAGE_TYPES = {
    "seminar": {
        "file": "seminar corp package.pdf",  # Default to corporate version if no specific match
        "description": "Seminar Package with accommodation options",
        "variants": {
            "corporate": "seminar corp package.pdf",
            "government": "seminar gov package.pdf"
        },
        # Keywords that suggest this package would be appropriate
        "keywords": [
            "retreat", "workshop", "seminar", "offsite", "residential",
            "overnight", "accommodation", "stay", "corporate retreat",
            "team building"
        ]
    },
    "meeting": {
        "file": "meeting corp package.pdf",  # Default to corporate version if no specific match
        "description": "Day meeting package without accommodation",
        "variants": {
            "corporate": "meeting corp package.pdf",
            "government": "meeting gov package.pdf"
        },
        # Keywords that suggest this package would be appropriate
        "keywords": [
            "meeting", "conference", "day event", "business meeting",
            "boardroom", "day seminar", "presentation", "training session",
            "client meeting", "executive"
        ]
    },
    "camping": {
        "file": "camping package.pdf",
        "description": "Outdoor camping and adventure package",
        "variants": {
            "corporate": "camping package.pdf",
            "university": "camping package.pdf",
            "government": "camping package.pdf",
            "school": "camping package.pdf"
        },
        # Keywords that suggest this package would be appropriate
        "keywords": [
            "camping", "outdoor", "adventure", "team building", "nature",
            "retreat", "field trip", "expedition", "outdoor activities",
            "student camp", "youth program"
        ]
    },
    "wedding": {
        "file": "wedding package.pdf",
        "description": "Wedding and celebration package",
        "variants": {
            "corporate": "wedding package.pdf",
            "university": "wedding package.pdf",
            "government": "wedding package.pdf",
            "school": "wedding package.pdf"
        },
        # Keywords that suggest this package would be appropriate
        "keywords": [
            "wedding", "celebration", "ceremony", "reception", "event",
            "party", "banquet", "gala", "anniversary", "special occasion",
            "formal dinner", "celebration"
        ]
    }
}

# Mappings between email templates and the most appropriate package types
TEMPLATE_TO_PACKAGE = {
    "default": "meeting",          # Default business template -> Meeting package
    "government": "seminar",       # Government agency template -> Seminar package
    "university": "camping",       # University/academic template -> Camping package
    "retreat": "seminar",          # Strategic retreat template -> Seminar package
    "cost": "meeting",             # Cost optimization template -> Meeting package
    "exec_tone": "meeting"         # Executive formal template -> Meeting package
}

# Organization type classification rules
ORGANIZATION_TYPES = {
    "corporate": [
        "sdn bhd", "berhad", "limited", "llc", "inc", "corporation", "corp", 
        "pte ltd", "private limited", "enterprise", "company", "consulting",
        "agency", "firm", "partners", "associates", "group"
    ],
    "government": [
        "ministry", "department", "jabatan", "kementerian", "gov", "govt",
        "pejabat", "suruhanjaya", "council", "authority", "board", "commission",
        "public sector", "majlis", "agensi", "negeri", "federal", "pusat"
    ],
    "university": [
        "university", "universiti", "college", "kolej", "institute", "institut",
        "campus", "faculty", "school of", "academic", "education", "higher education",
        "graduate school", "polytechnic", "research center"
    ],
    "school": [
        "school", "sekolah", "academy", "akademi", "primary school", "secondary school",
        "high school", "middle school", "elementary", "kindergarten", "tadika", 
        "preschool", "education center"
    ]
}

def get_package_pdf(lead_data: Dict[str, Any], template_name: Optional[str] = None) -> Optional[str]:
    """
    Determine the appropriate PDF package based on lead characteristics and template.
    
    Args:
        lead_data: Dictionary containing lead information
        template_name: Optional email template name used for this lead
        
    Returns:
        Path to the recommended PDF file or None if no match
    """
    # Detect organization type
    org_type = determine_organization_type(lead_data)
    
    # If template_name is provided, use the mapping to get the suggested package
    if template_name and template_name in TEMPLATE_TO_PACKAGE:
        package_type = TEMPLATE_TO_PACKAGE[template_name]
    else:
        # Otherwise determine best package based on keywords and other lead attributes
        package_type = determine_package_type(lead_data)
    
    if not package_type:
        # Default to meeting package if nothing else matches
        package_type = "meeting"
        
    # Get the specific variant based on organization type
    package_info = PACKAGE_TYPES[package_type]
    
    # If there's a specific variant for this org type, use it
    if org_type in package_info["variants"]:
        pdf_file = package_info["variants"][org_type]
    else:
        # Fall back to the default package PDF
        pdf_file = package_info["file"]
    
    pdf_path = PROPOSALS_DIR / pdf_file
    
    # Return None if file doesn't exist yet
    if not pdf_path.exists():
        return None
        
    return str(pdf_path)

def determine_organization_type(lead_data: Dict[str, Any]) -> str:
    """
    Determine the type of organization from lead data.
    
    Args:
        lead_data: Dictionary containing lead information
        
    Returns:
        Organization type (corporate, government, university, school)
    """
    organization = lead_data.get("organization", "").lower()
    
    # Check source URL for indicators
    source_url = lead_data.get("source_url", "").lower()
    
    # Check each type in priority order
    for org_type, keywords in ORGANIZATION_TYPES.items():
        for keyword in keywords:
            if keyword.lower() in organization or keyword.lower() in source_url:
                return org_type
    
    # Default to corporate if no clear match
    return "corporate"

def determine_package_type(lead_data: Dict[str, Any]) -> Optional[str]:
    """
    Determine the most appropriate package type for this lead.
    
    Args:
        lead_data: Dictionary containing lead information
        
    Returns:
        Package type key or None if no clear match
    """
    # Get relevant text to analyze
    org = lead_data.get("organization", "").lower()
    role = lead_data.get("role", "").lower()
    notes = lead_data.get("notes", "").lower()
    source = lead_data.get("source_url", "").lower()
    
    # Combine all text for keyword matching
    all_text = f"{org} {role} {notes} {source}"
    
    # Count keyword matches for each package type
    match_scores = {pkg_type: 0 for pkg_type in PACKAGE_TYPES.keys()}
    
    for pkg_type, pkg_info in PACKAGE_TYPES.items():
        for keyword in pkg_info["keywords"]:
            if keyword.lower() in all_text:
                match_scores[pkg_type] += 1
    
    # Find the package with the highest match score
    best_match = max(match_scores.items(), key=lambda x: x[1])
    
    # If there are no matches at all, return None
    if best_match[1] == 0:
        return None
        
    return best_match[0]

def list_available_packages() -> List[Dict[str, Any]]:
    """
    List all available packages that have valid PDF files.
    
    Returns:
        List of package information dictionaries
    """
    available_packages = []
    
    for pkg_type, pkg_info in PACKAGE_TYPES.items():
        # Check if main package file exists
        main_file_path = PROPOSALS_DIR / pkg_info["file"]
        
        pkg_data = {
            "type": pkg_type,
            "description": pkg_info["description"],
            "main_file": str(main_file_path) if main_file_path.exists() else None,
            "variants": {}
        }
        
        # Check which variants exist
        for variant_type, variant_file in pkg_info["variants"].items():
            variant_path = PROPOSALS_DIR / variant_file
            if variant_path.exists():
                pkg_data["variants"][variant_type] = str(variant_path)
        
        # Add to available list if at least one variant exists
        if pkg_data["main_file"] or pkg_data["variants"]:
            available_packages.append(pkg_data)
    
    return available_packages 