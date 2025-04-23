#!/usr/bin/env python3
"""
Cache utility for email generation and deduplication.

This module provides functionality to:
- Cache generated emails to avoid duplicates
- Track email generation history
- Manage generation limits per lead
"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EmailCache:
    """Manages caching of generated emails and deduplication."""
    
    def __init__(self, cache_dir: str = "cache", max_generations: int = 3):
        """
        Initialize the email cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_generations: Maximum number of generations allowed per lead
        """
        self.cache_dir = cache_dir
        self.max_generations = max_generations
        self.cache_file = os.path.join(cache_dir, "email_cache.json")
        self.generation_history = self._load_cache()
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def _load_cache(self) -> Dict:
        """Load the cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save the cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.generation_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _generate_hash(self, lead: Dict, template_name: str) -> str:
        """Generate a unique hash for a lead and template combination."""
        # Create a string representation of the relevant lead data
        lead_str = f"{lead.get('email', '')}_{lead.get('organization', '')}_{template_name}"
        return hashlib.md5(lead_str.encode()).hexdigest()
    
    def can_generate(self, lead: Dict, template_name: str) -> bool:
        """
        Check if an email can be generated for this lead.
        
        Args:
            lead: Dictionary containing lead information
            template_name: Name of the template to use
            
        Returns:
            True if email can be generated, False otherwise
        """
        lead_hash = self._generate_hash(lead, template_name)
        
        # Check if lead exists in cache
        if lead_hash in self.generation_history:
            history = self.generation_history[lead_hash]
            
            # Check if max generations reached
            if len(history) >= self.max_generations:
                logger.warning(f"Max generations ({self.max_generations}) reached for lead: {lead.get('email')}")
                return False
            
            # Check if last generation was too recent (e.g., within 30 days)
            last_generation = datetime.fromisoformat(history[-1]["generated_at"])
            if datetime.now() - last_generation < timedelta(days=30):
                logger.warning(f"Recent generation exists for lead: {lead.get('email')}")
                return False
        
        return True
    
    def record_generation(self, lead: Dict, template_name: str, email_data: Dict):
        """
        Record a new email generation in the cache.
        
        Args:
            lead: Dictionary containing lead information
            template_name: Name of the template used
            email_data: Dictionary containing the generated email
        """
        lead_hash = self._generate_hash(lead, template_name)
        
        if lead_hash not in self.generation_history:
            self.generation_history[lead_hash] = []
        
        # Add generation record
        self.generation_history[lead_hash].append({
            "generated_at": email_data["generated_at"],
            "template_used": template_name,
            "subject": email_data["subject"]
        })
        
        # Save cache
        self._save_cache()
    
    def get_generation_history(self, lead: Dict, template_name: str) -> List[Dict]:
        """
        Get generation history for a lead.
        
        Args:
            lead: Dictionary containing lead information
            template_name: Name of the template used
            
        Returns:
            List of generation records
        """
        lead_hash = self._generate_hash(lead, template_name)
        return self.generation_history.get(lead_hash, [])
    
    def clear_cache(self):
        """Clear the entire cache."""
        self.generation_history = {}
        self._save_cache()
        logger.info("Cache cleared") 