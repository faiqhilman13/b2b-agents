#!/usr/bin/env python3
"""
Email Generator Module

This module handles the generation of personalized emails for lead outreach.
It uses templates from the prompts directory and personalizes them based on
the lead's information.
"""

import os
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class EmailGenerator:
    """Handles the generation of personalized emails for lead outreach."""
    
    def __init__(self, templates_dir: str = "prompts"):
        """
        Initialize the EmailGenerator.
        
        Args:
            templates_dir: Directory containing email templates
        """
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
        logger.info(f"EmailGenerator initialized with {len(self.templates)} templates")
    
    def _load_templates(self) -> Dict:
        """Load email templates from the templates directory."""
        templates = {}
        try:
            templates_path = os.path.join(os.path.dirname(__file__), "..", self.templates_dir)
            for filename in os.listdir(templates_path):
                if filename.endswith(".json"):
                    template_name = filename[:-5]  # Remove .json extension
                    with open(os.path.join(templates_path, filename), 'r', encoding='utf-8') as f:
                        templates[template_name] = json.load(f)
            logger.info(f"Loaded {len(templates)} email templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            templates = {}
        return templates
    
    def generate_email(self, 
                      lead: Dict,
                      template_name: str = "default",
                      custom_variables: Optional[Dict] = None) -> Dict:
        """
        Generate a personalized email for a lead.
        
        Args:
            lead: Dictionary containing lead information
            template_name: Name of the template to use
            custom_variables: Additional variables to use in template
            
        Returns:
            Dictionary containing the generated email with subject and body
        """
        try:
            # Get the template
            template = self.templates.get(template_name)
            if not template:
                logger.warning(f"Template '{template_name}' not found, using default")
                template = self.templates.get("default")
            
            if not template:
                raise ValueError("No valid template found")
            
            # Create specialized sentences based on available data
            industry_sentence = ""
            if lead.get("industry"):
                industry_sentence = f"I noticed your focus on {lead.get('industry')}, which aligns with our expertise in [Your Relevant Expertise]."
            
            rating_sentence = ""
            if lead.get("rating") and float(lead.get("rating", 0)) >= 4.0:
                rating_sentence = f"I was impressed by your excellent rating of {lead.get('rating')} and the positive feedback from your clients."
            
            location_sentence = ""
            if lead.get("city") and lead.get("state"):
                location_sentence = f"As a business based in {lead.get('city')}, {lead.get('state')}, you're ideally positioned to benefit from our [Relevant Local Service/Insight]."
            
            social_sentence = ""
            if lead.get("social_media", {}).get("instagram") or lead.get("social_media", {}).get("facebook"):
                platforms = []
                if lead.get("social_media", {}).get("instagram"):
                    platforms.append("Instagram")
                if lead.get("social_media", {}).get("facebook"):
                    platforms.append("Facebook")
                if lead.get("social_media", {}).get("linkedin"):
                    platforms.append("LinkedIn")
                
                platform_text = " and ".join(platforms)
                social_sentence = f"I've been following your {platform_text} presence and am impressed with your engagement with customers."
            
            # Prepare variables for template
            variables = {
                "organization": lead.get("organization", ""),
                "person_name": lead.get("person_name", "Your Team"),
                "role": lead.get("role", ""),
                "email": lead.get("email", ""),
                "phone": lead.get("phone", ""),
                "address": lead.get("address", ""),
                "city": lead.get("city", "Malaysia"),
                "state": lead.get("state", ""),
                "postal_code": lead.get("postal_code", ""),
                "website": lead.get("website", ""),
                "industry": lead.get("industry", "your industry"),
                "rating": lead.get("rating", ""),
                "reviews_count": lead.get("reviews_count", ""),
                "industry_sentence": industry_sentence,
                "rating_sentence": rating_sentence,
                "location_sentence": location_sentence,
                "social_sentence": social_sentence,
                "current_date": datetime.now().strftime("%B %d, %Y"),
                **(custom_variables or {})
            }
            
            # Generate subject and body
            subject = self._fill_template(template["subject"], variables)
            body = self._fill_template(template["body"], variables)
            
            return {
                "subject": subject,
                "body": body,
                "to_email": lead.get("email", ""),
                "template_used": template_name,
                "generated_at": datetime.now().isoformat(),
                "organization": lead.get("organization", ""),
                "person_name": lead.get("person_name", ""),
                "role": lead.get("role", ""),
                "source_url": lead.get("source_url", ""),
                "notes": lead.get("notes", "")
            }
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            raise
    
    def _fill_template(self, template: str, variables: Dict) -> str:
        """Fill a template string with variables."""
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            return template
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def add_template(self, name: str, template: Dict) -> bool:
        """
        Add a new email template.
        
        Args:
            name: Name of the template
            template: Dictionary containing 'subject' and 'body' keys
            
        Returns:
            True if template was added successfully
        """
        try:
            if "subject" not in template or "body" not in template:
                raise ValueError("Template must contain 'subject' and 'body' keys")
            
            self.templates[name] = template
            logger.info(f"Added new template: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding template: {e}")
            return False 