"""API Service for Lead Generator.

This module connects the API layer with the core lead_generator components,
providing a unified interface for the Agentive frontend to interact with
the backend functionality.
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
import csv
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from lead_generator.database.models import Lead, EmailGeneration, LeadStatus, LeadStatusHistory, DashboardStats
from lead_generator.database.queries import LeadQueries
from lead_generator.agents.email_generator import EmailGenerator
from lead_generator.agents.email_sender import EmailSender, email_sender
from lead_generator.utils.cache import EmailCache
from lead_generator.config.email_config import EMAIL_TEMPLATES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lead_generator/logs/api_service.log")
    ]
)
logger = logging.getLogger(__name__)

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
EMAILS_DIR = BASE_DIR / "emails"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
EMAILS_DIR.mkdir(exist_ok=True)

class APIService:
    """Service layer connecting API routes to core functionality."""
    
    def __init__(self, db_session: Session):
        """Initialize the API service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.lead_queries = LeadQueries(db_session)
        self.email_generator = EmailGenerator()
        self.email_cache = EmailCache()
        logger.info("API Service initialized")
    
    def get_all_leads(self, 
                     status: Optional[LeadStatus] = None, 
                     source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all leads, optionally filtered by status or source.
        
        Args:
            status: Optional lead status filter
            source: Optional source filter
            
        Returns:
            List of leads as dictionaries
        """
        try:
            if status:
                leads = self.lead_queries.get_leads_by_status(status)
            else:
                # Get all leads from the database
                leads = self.db_session.query(Lead).all()
            
            # Convert to dictionaries
            lead_dicts = []
            for lead in leads:
                lead_dict = {
                    "id": lead.id,
                    "organization": lead.organization,
                    "person_name": lead.person_name,
                    "role": lead.role,
                    "email": lead.email,
                    "phone": lead.phone,
                    "source_url": lead.source_url,
                    "status": lead.status.value if lead.status else "new",
                    "created_at": lead.created_at.isoformat() if lead.created_at else None,
                    "updated_at": lead.updated_at.isoformat() if lead.updated_at else None
                }
                
                # Apply source filter if provided
                if source and source.lower() not in lead_dict.get("source_url", "").lower():
                    continue
                
                lead_dicts.append(lead_dict)
            
            logger.info(f"Retrieved {len(lead_dicts)} leads")
            return lead_dicts
        except Exception as e:
            logger.error(f"Error retrieving leads: {str(e)}")
            raise
    
    def get_lead_by_id(self, lead_id: int) -> Dict[str, Any]:
        """Get a lead by ID.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead as dictionary
            
        Raises:
            HTTPException: If lead not found
        """
        lead = self.db_session.query(Lead).get(lead_id)
        if not lead:
            logger.warning(f"Lead with ID {lead_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {lead_id} not found"
            )
        
        # Get email generations for this lead
        generations = self.lead_queries.get_lead_generations(lead_id)
        
        # Get status history
        status_history = self.lead_queries.get_lead_status_history(lead_id)
        
        # Convert to dictionary
        lead_dict = {
            "id": lead.id,
            "organization": lead.organization,
            "person_name": lead.person_name,
            "role": lead.role,
            "email": lead.email,
            "phone": lead.phone,
            "source_url": lead.source_url,
            "status": lead.status.value if lead.status else "new",
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            "email_generations": [
                {
                    "id": gen.id,
                    "template_name": gen.template_name,
                    "subject": gen.subject,
                    "generated_at": gen.generated_at.isoformat() if gen.generated_at else None,
                    "sent_at": gen.sent_at.isoformat() if gen.sent_at else None,
                    "response_received": gen.response_received.isoformat() if gen.response_received else None
                }
                for gen in generations
            ],
            "status_history": [
                {
                    "id": history.id,
                    "old_status": history.old_status.value if history.old_status else None,
                    "new_status": history.new_status.value,
                    "changed_at": history.changed_at.isoformat() if history.changed_at else None,
                    "notes": history.notes
                }
                for history in status_history
            ]
        }
        
        logger.info(f"Retrieved lead with ID {lead_id}")
        return lead_dict
    
    def update_lead_status(self, 
                          lead_id: int, 
                          new_status: LeadStatus, 
                          notes: Optional[str] = None) -> Dict[str, Any]:
        """Update a lead's status.
        
        Args:
            lead_id: Lead ID
            new_status: New status
            notes: Optional notes about the status change
            
        Returns:
            Updated lead as dictionary
            
        Raises:
            HTTPException: If lead not found
        """
        lead = self.db_session.query(Lead).get(lead_id)
        if not lead:
            logger.warning(f"Lead with ID {lead_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {lead_id} not found"
            )
        
        # Update lead status
        old_status = lead.status
        self.lead_queries.update_lead_status(lead_id, new_status, notes)
        
        # Update dashboard stats
        self._update_dashboard_stats(old_status, new_status)
        
        logger.info(f"Updated lead {lead_id} status from {old_status} to {new_status}")
        
        # Return updated lead
        return self.get_lead_by_id(lead_id)
    
    def _update_dashboard_stats(self, old_status: Optional[LeadStatus], new_status: LeadStatus):
        """Update dashboard statistics based on status change.
        
        Args:
            old_status: Previous status
            new_status: New status
        """
        today = date.today()
        stats = self.db_session.query(DashboardStats).filter(
            DashboardStats.stat_date == today
        ).first()
        
        if not stats:
            # Create new stats for today
            stats = DashboardStats(stat_date=today)
            self.db_session.add(stats)
        
        # Update relevant counters based on status changes
        if new_status == LeadStatus.BOOKED and (old_status != LeadStatus.BOOKED):
            stats.meetings_booked += 1
        
        if new_status == LeadStatus.RESPONDED and (old_status != LeadStatus.RESPONDED):
            stats.responses_received += 1
        
        # Save changes
        self.db_session.commit()
    
    def generate_email(self, 
                      lead_id: int, 
                      template_name: str = "default",
                      custom_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate an email for a lead.
        
        Args:
            lead_id: Lead ID
            template_name: Template name
            custom_variables: Custom variables for template
            
        Returns:
            Generated email
            
        Raises:
            HTTPException: If lead not found or email generation fails
        """
        # Get the lead
        lead = self.db_session.query(Lead).get(lead_id)
        if not lead:
            logger.warning(f"Lead with ID {lead_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {lead_id} not found"
            )
        
        # Convert lead to dictionary for email generator
        lead_dict = {
            "organization": lead.organization,
            "person_name": lead.person_name,
            "role": lead.role,
            "email": lead.email
        }
        
        try:
            # Check if we can generate an email (deduplication check)
            if not self.email_cache.can_generate(lead_dict, template_name):
                logger.warning(f"Email generation limit reached for lead {lead_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email generation limit reached for this lead"
                )
            
            # Generate the email
            email_data = self.email_generator.generate_email(
                lead=lead_dict,
                template_name=template_name,
                custom_variables=custom_variables
            )
            
            # Record the generation in cache
            self.email_cache.record_generation(lead_dict, template_name, email_data)
            
            # Save to database
            generation = self.lead_queries.save_email_generation(lead_id, email_data)
            
            # Save email to file
            email_path = EMAILS_DIR / f"{lead_id}_{template_name}.txt"
            with open(email_path, "w", encoding="utf-8") as f:
                f.write(f"Subject: {email_data['subject']}\n\n")
                f.write(email_data['body'])
            
            # Return the generated email
            result = {
                "generation_id": generation.id,
                "lead_id": lead_id,
                "template_name": template_name,
                "subject": email_data["subject"],
                "body": email_data["body"],
                "to_email": email_data["to_email"],
                "generated_at": email_data["generated_at"],
                "file_path": str(email_path)
            }
            
            logger.info(f"Generated email for lead {lead_id} using template {template_name}")
            return result
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating email: {str(e)}"
            )
    
    def send_email(self, 
                  generation_id: int, 
                  background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Send a generated email.
        
        Args:
            generation_id: Email generation ID
            background_tasks: FastAPI background tasks
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If email generation not found or sending fails
        """
        # Get the email generation
        generation = self.db_session.query(EmailGeneration).get(generation_id)
        if not generation:
            logger.warning(f"Email generation with ID {generation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email generation with ID {generation_id} not found"
            )
        
        # Get the lead
        lead = self.db_session.query(Lead).get(generation.lead_id)
        if not lead or not lead.email:
            logger.warning(f"Lead with ID {generation.lead_id} not found or has no email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lead not found or has no email address"
            )
        
        try:
            # Send the email in the background
            background_tasks.add_task(
                self._send_email_task,
                to_email=lead.email,
                subject=generation.subject,
                body=generation.body,
                generation_id=generation_id
            )
            
            # Update lead status
            self.lead_queries.update_lead_status(
                lead.id, 
                LeadStatus.CONTACTED, 
                f"Email sent using template: {generation.template_name}"
            )
            
            # Update dashboard stats
            today = date.today()
            stats = self.db_session.query(DashboardStats).filter(
                DashboardStats.stat_date == today
            ).first()
            
            if not stats:
                # Create new stats for today
                stats = DashboardStats(stat_date=today)
                self.db_session.add(stats)
            
            stats.emails_sent += 1
            self.db_session.commit()
            
            logger.info(f"Email sending scheduled for lead {lead.id}")
            return {
                "message": f"Email sending scheduled to {lead.email}",
                "generation_id": generation_id,
                "lead_id": lead.id
            }
        except Exception as e:
            logger.error(f"Error scheduling email: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error scheduling email: {str(e)}"
            )
    
    async def _send_email_task(self, to_email: str, subject: str, body: str, generation_id: int):
        """Background task to send an email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            generation_id: Email generation ID
        """
        try:
            with email_sender() as sender:
                # Send the email
                success = sender.send_email(to_email, subject, body)
            
            if success:
                # Mark email as sent
                self.lead_queries.mark_email_sent(generation_id)
                logger.info(f"Email sent successfully to {to_email}")
            else:
                logger.error(f"Failed to send email to {to_email}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics.
        
        Returns:
            Dashboard statistics
        """
        try:
            # Get today's stats
            today = date.today()
            stats = self.db_session.query(DashboardStats).filter(
                DashboardStats.stat_date == today
            ).first()
            
            if not stats:
                # Create new stats for today
                stats = DashboardStats(stat_date=today)
                self.db_session.add(stats)
                self.db_session.commit()
            
            # Get leads by status
            status_counts = {}
            for status in LeadStatus:
                count = self.db_session.query(Lead).filter(Lead.status == status).count()
                status_counts[status.value] = count
            
            # Get recent email generations
            recent_generations = self.db_session.query(EmailGeneration)\
                .order_by(EmailGeneration.generated_at.desc())\
                .limit(10)\
                .all()
            
            # Get available templates
            available_templates = list(EMAIL_TEMPLATES.keys())
            
            # Compile statistics
            result = {
                "date": today.isoformat(),
                "emails_sent": stats.emails_sent,
                "emails_opened": stats.emails_opened,
                "responses_received": stats.responses_received,
                "meetings_booked": stats.meetings_booked,
                "leads_by_status": status_counts,
                "recent_generations": [
                    {
                        "id": gen.id,
                        "lead_id": gen.lead_id,
                        "template_name": gen.template_name,
                        "subject": gen.subject,
                        "generated_at": gen.generated_at.isoformat() if gen.generated_at else None,
                        "sent_at": gen.sent_at.isoformat() if gen.sent_at else None
                    }
                    for gen in recent_generations
                ],
                "available_templates": available_templates
            }
            
            logger.info("Retrieved dashboard statistics")
            return result
        except Exception as e:
            logger.error(f"Error retrieving dashboard statistics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving dashboard statistics: {str(e)}"
            )
    
    def export_leads_to_csv(self, 
                           output_file: Optional[str] = None, 
                           statuses: Optional[List[LeadStatus]] = None) -> Dict[str, Any]:
        """Export leads to CSV.
        
        Args:
            output_file: Output file name
            statuses: List of statuses to include
            
        Returns:
            Export result
        """
        try:
            # Default output file
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = str(OUTPUT_DIR / f"leads_export_{timestamp}.csv")
            
            # Get leads
            query = self.db_session.query(Lead)
            
            # Filter by status if provided
            if statuses:
                query = query.filter(Lead.status.in_(statuses))
            
            leads = query.all()
            
            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'organization', 'person_name', 'role', 
                    'email', 'phone', 'source_url', 'status', 
                    'created_at', 'updated_at'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for lead in leads:
                    writer.writerow({
                        'id': lead.id,
                        'organization': lead.organization,
                        'person_name': lead.person_name,
                        'role': lead.role,
                        'email': lead.email,
                        'phone': lead.phone,
                        'source_url': lead.source_url,
                        'status': lead.status.value if lead.status else 'new',
                        'created_at': lead.created_at.isoformat() if lead.created_at else '',
                        'updated_at': lead.updated_at.isoformat() if lead.updated_at else ''
                    })
            
            logger.info(f"Exported {len(leads)} leads to {output_file}")
            return {
                "success": True,
                "file_path": output_file,
                "lead_count": len(leads)
            }
        except Exception as e:
            logger.error(f"Error exporting leads: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exporting leads: {str(e)}"
            ) 