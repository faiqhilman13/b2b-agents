#!/usr/bin/env python3
"""
Database queries for the lead generator.

This module provides functions for:
- Saving and retrieving leads
- Managing email generations
- Tracking lead status
- Querying generation history
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import Lead, EmailGeneration, LeadStatusHistory, LeadStatus

class LeadQueries:
    """Handles database operations for leads and email generations."""
    
    def __init__(self, session: Session):
        """Initialize with a SQLAlchemy session."""
        self.session = session
    
    def save_lead(self, lead_data: Dict) -> Lead:
        """
        Save a new lead to the database.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            The saved Lead object
        """
        lead = Lead(
            organization=lead_data.get('organization'),
            person_name=lead_data.get('person_name'),
            role=lead_data.get('role'),
            email=lead_data.get('email'),
            phone=lead_data.get('phone'),
            source_url=lead_data.get('source_url')
        )
        
        self.session.add(lead)
        self.session.commit()
        return lead
    
    def get_lead(self, email: str) -> Optional[Lead]:
        """Get a lead by email address."""
        return self.session.query(Lead).filter(Lead.email == email).first()
    
    def save_email_generation(self, lead_id: int, email_data: Dict) -> EmailGeneration:
        """
        Save a generated email to the database.
        
        Args:
            lead_id: ID of the lead
            email_data: Dictionary containing email information
            
        Returns:
            The saved EmailGeneration object
        """
        generation = EmailGeneration(
            lead_id=lead_id,
            template_name=email_data['template_used'],
            subject=email_data['subject'],
            body=email_data['body'],
            generated_at=datetime.fromisoformat(email_data['generated_at'])
        )
        
        self.session.add(generation)
        self.session.commit()
        return generation
    
    def update_lead_status(self, lead_id: int, new_status: LeadStatus, notes: Optional[str] = None):
        """
        Update a lead's status and record the change in history.
        
        Args:
            lead_id: ID of the lead
            new_status: New status to set
            notes: Optional notes about the status change
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            return
        
        old_status = lead.status
        lead.status = new_status
        
        # Record status change
        history = LeadStatusHistory(
            lead_id=lead_id,
            old_status=old_status,
            new_status=new_status,
            notes=notes
        )
        
        self.session.add(history)
        self.session.commit()
    
    def get_lead_generations(self, lead_id: int) -> List[EmailGeneration]:
        """Get all email generations for a lead."""
        return self.session.query(EmailGeneration)\
            .filter(EmailGeneration.lead_id == lead_id)\
            .order_by(desc(EmailGeneration.generated_at))\
            .all()
    
    def get_leads_by_status(self, status: LeadStatus) -> List[Lead]:
        """Get all leads with a specific status."""
        return self.session.query(Lead)\
            .filter(Lead.status == status)\
            .order_by(desc(Lead.updated_at))\
            .all()
    
    def get_lead_status_history(self, lead_id: int) -> List[LeadStatusHistory]:
        """Get the status history for a lead."""
        return self.session.query(LeadStatusHistory)\
            .filter(LeadStatusHistory.lead_id == lead_id)\
            .order_by(desc(LeadStatusHistory.changed_at))\
            .all()
    
    def mark_email_sent(self, generation_id: int):
        """Mark an email generation as sent."""
        generation = self.session.query(EmailGeneration).get(generation_id)
        if generation:
            generation.sent_at = datetime.utcnow()
            self.session.commit()
    
    def mark_response_received(self, generation_id: int):
        """Mark that a response was received for an email."""
        generation = self.session.query(EmailGeneration).get(generation_id)
        if generation:
            generation.response_received = datetime.utcnow()
            self.session.commit() 