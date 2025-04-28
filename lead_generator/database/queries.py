#!/usr/bin/env python3
"""
Database queries for the lead generator.

This module provides functions for:
- Saving and retrieving leads
- Managing email generations
- Tracking lead status
- Querying generation history
- Managing social media profiles
- Storing and retrieving location data
- Handling business details
- Tracking data sources
"""

import json
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, func

from .models import (
    Lead, 
    EmailGeneration, 
    LeadStatusHistory, 
    LeadStatus,
    SocialMediaProfile,
    Location,
    BusinessDetail,
    LeadDataSource,
    DataSource,
    Tag
)

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
        source_type = lead_data.get('source', 'manual')
        if isinstance(source_type, str) and hasattr(DataSource, source_type.upper()):
            source = getattr(DataSource, source_type.upper())
        else:
            source = DataSource.MANUAL
            
        lead = Lead(
            organization=lead_data.get('organization'),
            person_name=lead_data.get('person_name'),
            role=lead_data.get('role'),
            email=lead_data.get('email'),
            alternative_emails=lead_data.get('alternative_emails'),
            phone=lead_data.get('phone'),
            alternative_phones=lead_data.get('alternative_phones'),
            website=lead_data.get('website'),
            industry=lead_data.get('industry'),
            source=source,
            source_url=lead_data.get('source_url'),
            notes=lead_data.get('notes'),
            completeness_score=lead_data.get('completeness_score', 0.0)
        )
        
        self.session.add(lead)
        self.session.commit()
        
        # Add location if provided
        if lead_data.get('address') or lead_data.get('city') or lead_data.get('latitude'):
            self.add_lead_location(lead.id, lead_data)
            
        # Add business details if provided
        if lead_data.get('rating') or lead_data.get('category'):
            self.add_business_details(lead.id, lead_data)
            
        # Add social media profiles if provided
        if social_media := lead_data.get('social_media', {}):
            for platform, url in social_media.items():
                if url:
                    self.add_social_media_profile(lead.id, platform, url)
                    
        # Add data source information if provided
        if raw_data := lead_data.get('raw_data'):
            self.add_lead_data_source(
                lead.id, 
                source_type=source, 
                source_url=lead_data.get('source_url'),
                raw_data=raw_data
            )
            
        return lead
    
    def update_lead(self, lead_id: int, lead_data: Dict) -> Optional[Lead]:
        """
        Update an existing lead with new data.
        
        Args:
            lead_id: ID of the lead to update
            lead_data: Dictionary containing updated lead information
            
        Returns:
            The updated Lead object or None if not found
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            return None
            
        # Update basic lead information
        if 'organization' in lead_data:
            lead.organization = lead_data['organization']
        if 'person_name' in lead_data:
            lead.person_name = lead_data['person_name']
        if 'role' in lead_data:
            lead.role = lead_data['role']
        if 'email' in lead_data:
            lead.email = lead_data['email']
        if 'alternative_emails' in lead_data:
            lead.alternative_emails = lead_data['alternative_emails']
        if 'phone' in lead_data:
            lead.phone = lead_data['phone']
        if 'alternative_phones' in lead_data:
            lead.alternative_phones = lead_data['alternative_phones']
        if 'website' in lead_data:
            lead.website = lead_data['website']
        if 'industry' in lead_data:
            lead.industry = lead_data['industry']
        if 'notes' in lead_data:
            lead.notes = lead_data['notes']
        if 'completeness_score' in lead_data:
            lead.completeness_score = lead_data['completeness_score']
            
        lead.updated_at = datetime.utcnow()
        self.session.commit()
        
        # Update or add location if provided
        if any(key in lead_data for key in ['address', 'city', 'latitude', 'longitude']):
            # Update primary location if it exists, otherwise add a new one
            primary_location = self.session.query(Location)\
                .filter(Location.lead_id == lead_id, Location.is_primary == True)\
                .first()
                
            if primary_location:
                self.update_lead_location(primary_location.id, lead_data)
            else:
                self.add_lead_location(lead_id, lead_data)
                
        # Update or add business details if provided
        if any(key in lead_data for key in ['rating', 'category', 'reviews_count']):
            business_detail = self.session.query(BusinessDetail)\
                .filter(BusinessDetail.lead_id == lead_id)\
                .first()
                
            if business_detail:
                self.update_business_details(business_detail.id, lead_data)
            else:
                self.add_business_details(lead_id, lead_data)
                
        # Add social media profiles if provided
        if social_media := lead_data.get('social_media', {}):
            for platform, url in social_media.items():
                if url:
                    # Check if profile already exists
                    existing = self.session.query(SocialMediaProfile)\
                        .join(SocialMediaProfile.leads)\
                        .filter(
                            Lead.id == lead_id,
                            SocialMediaProfile.platform == platform
                        ).first()
                        
                    if existing:
                        existing.url = url
                        existing.last_updated = datetime.utcnow()
                    else:
                        self.add_social_media_profile(lead_id, platform, url)
            
            self.session.commit()
            
        return lead
    
    def get_lead(self, lead_id: int = None, email: str = None) -> Optional[Lead]:
        """
        Get a lead by ID or email address.
        
        Args:
            lead_id: ID of the lead (optional)
            email: Email address of the lead (optional)
            
        Returns:
            Lead object or None if not found
        """
        query = self.session.query(Lead)
        
        # Load related data
        query = query.options(
            joinedload(Lead.social_media_profiles),
            joinedload(Lead.locations),
            joinedload(Lead.business_detail),
            joinedload(Lead.tags)
        )
        
        if lead_id:
            return query.filter(Lead.id == lead_id).first()
        elif email:
            return query.filter(Lead.email == email).first()
        return None
    
    def search_leads(self, search_term: str = None, status: LeadStatus = None, 
                    source: DataSource = None, min_score: float = None,
                    limit: int = 100, offset: int = 0) -> List[Lead]:
        """
        Search for leads with various filters.
        
        Args:
            search_term: Search term to match against organization, name, email, etc.
            status: Filter by lead status
            source: Filter by data source
            min_score: Minimum completeness score
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of matching Lead objects
        """
        query = self.session.query(Lead)
        
        # Apply filters
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Lead.organization.ilike(search_pattern),
                    Lead.person_name.ilike(search_pattern),
                    Lead.email.ilike(search_pattern),
                    Lead.phone.ilike(search_pattern),
                    Lead.industry.ilike(search_pattern)
                )
            )
            
        if status:
            query = query.filter(Lead.status == status)
            
        if source:
            query = query.filter(Lead.source == source)
            
        if min_score is not None:
            query = query.filter(Lead.completeness_score >= min_score)
            
        # Apply pagination and ordering
        return query.order_by(desc(Lead.updated_at)).limit(limit).offset(offset).all()
    
    def add_social_media_profile(self, lead_id: int, platform: str, 
                                url: str, username: str = None,
                                followers_count: int = None, 
                                following_count: int = None,
                                is_verified: bool = None) -> SocialMediaProfile:
        """
        Add a social media profile to a lead.
        
        Args:
            lead_id: ID of the lead
            platform: Social media platform name
            url: Profile URL
            username: Username (optional)
            followers_count: Number of followers (optional)
            following_count: Number of accounts followed (optional)
            is_verified: Whether the account is verified (optional)
            
        Returns:
            The created SocialMediaProfile object
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        # Extract username from URL if not provided
        if not username and platform == "instagram" and "/" in url:
            username = url.rstrip("/").split("/")[-1]
            
        profile = SocialMediaProfile(
            platform=platform,
            url=url,
            username=username,
            followers_count=followers_count or 0,
            following_count=following_count or 0,
            is_verified=is_verified or False
        )
        
        lead.social_media_profiles.append(profile)
        self.session.commit()
        return profile
    
    def get_social_media_profiles(self, lead_id: int) -> List[SocialMediaProfile]:
        """
        Get all social media profiles for a lead.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            List of SocialMediaProfile objects
        """
        return self.session.query(SocialMediaProfile)\
            .join(SocialMediaProfile.leads)\
            .filter(Lead.id == lead_id)\
            .all()
    
    def add_lead_location(self, lead_id: int, location_data: Dict) -> Location:
        """
        Add a location to a lead.
        
        Args:
            lead_id: ID of the lead
            location_data: Dictionary containing location information
            
        Returns:
            The created Location object
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        # Check if this is the first location and set as primary if so
        existing_locations = self.session.query(Location)\
            .filter(Location.lead_id == lead_id)\
            .count()
        is_primary = existing_locations == 0
        
        location = Location(
            lead_id=lead_id,
            address=location_data.get('address'),
            street=location_data.get('street'),
            city=location_data.get('city'),
            state=location_data.get('state'),
            postal_code=location_data.get('postal_code'),
            country=location_data.get('country', 'Malaysia'),
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude'),
            is_primary=is_primary
        )
        
        self.session.add(location)
        self.session.commit()
        return location
    
    def update_lead_location(self, location_id: int, location_data: Dict) -> Optional[Location]:
        """
        Update an existing location.
        
        Args:
            location_id: ID of the location to update
            location_data: Dictionary containing updated location information
            
        Returns:
            The updated Location object or None if not found
        """
        location = self.session.query(Location).get(location_id)
        if not location:
            return None
            
        if 'address' in location_data:
            location.address = location_data['address']
        if 'street' in location_data:
            location.street = location_data['street']
        if 'city' in location_data:
            location.city = location_data['city']
        if 'state' in location_data:
            location.state = location_data['state']
        if 'postal_code' in location_data:
            location.postal_code = location_data['postal_code']
        if 'country' in location_data:
            location.country = location_data['country']
        if 'latitude' in location_data:
            location.latitude = location_data['latitude']
        if 'longitude' in location_data:
            location.longitude = location_data['longitude']
            
        location.updated_at = datetime.utcnow()
        self.session.commit()
        return location
    
    def add_business_details(self, lead_id: int, detail_data: Dict) -> BusinessDetail:
        """
        Add business details to a lead.
        
        Args:
            lead_id: ID of the lead
            detail_data: Dictionary containing business details
            
        Returns:
            The created BusinessDetail object
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        # Check if details already exist
        existing = self.session.query(BusinessDetail)\
            .filter(BusinessDetail.lead_id == lead_id)\
            .first()
            
        if existing:
            return self.update_business_details(existing.id, detail_data)
            
        business_detail = BusinessDetail(
            lead_id=lead_id,
            rating=detail_data.get('rating'),
            reviews_count=detail_data.get('reviews_count'),
            price_level=detail_data.get('price_level'),
            category=detail_data.get('category'),
            subcategories=detail_data.get('subcategories'),
            year_established=detail_data.get('year_established'),
            employee_count=detail_data.get('employee_count'),
            services=detail_data.get('services'),
            products=detail_data.get('products'),
            business_hours=detail_data.get('business_hours'),
            description=detail_data.get('description')
        )
        
        self.session.add(business_detail)
        self.session.commit()
        return business_detail
    
    def update_business_details(self, detail_id: int, detail_data: Dict) -> Optional[BusinessDetail]:
        """
        Update existing business details.
        
        Args:
            detail_id: ID of the business details to update
            detail_data: Dictionary containing updated business details
            
        Returns:
            The updated BusinessDetail object or None if not found
        """
        detail = self.session.query(BusinessDetail).get(detail_id)
        if not detail:
            return None
            
        if 'rating' in detail_data:
            detail.rating = detail_data['rating']
        if 'reviews_count' in detail_data:
            detail.reviews_count = detail_data['reviews_count']
        if 'price_level' in detail_data:
            detail.price_level = detail_data['price_level']
        if 'category' in detail_data:
            detail.category = detail_data['category']
        if 'subcategories' in detail_data:
            detail.subcategories = detail_data['subcategories']
        if 'year_established' in detail_data:
            detail.year_established = detail_data['year_established']
        if 'employee_count' in detail_data:
            detail.employee_count = detail_data['employee_count']
        if 'services' in detail_data:
            detail.services = detail_data['services']
        if 'products' in detail_data:
            detail.products = detail_data['products']
        if 'business_hours' in detail_data:
            detail.business_hours = detail_data['business_hours']
        if 'description' in detail_data:
            detail.description = detail_data['description']
            
        detail.updated_at = datetime.utcnow()
        self.session.commit()
        return detail
    
    def add_lead_data_source(self, lead_id: int, source_type: Union[DataSource, str], 
                           source_url: str = None, raw_data: Any = None) -> LeadDataSource:
        """
        Add data source information to a lead.
        
        Args:
            lead_id: ID of the lead
            source_type: Type of data source
            source_url: Source URL (optional)
            raw_data: Raw data from the source (optional)
            
        Returns:
            The created LeadDataSource object
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        if isinstance(source_type, str) and hasattr(DataSource, source_type.upper()):
            source_type = getattr(DataSource, source_type.upper())
        elif not isinstance(source_type, DataSource):
            source_type = DataSource.OTHER
            
        # Convert raw_data to JSON string if it's not already a string
        if raw_data and not isinstance(raw_data, str):
            raw_data = json.dumps(raw_data)
            
        data_source = LeadDataSource(
            lead_id=lead_id,
            source_type=source_type,
            source_url=source_url,
            raw_data=raw_data,
            data_timestamp=datetime.utcnow()
        )
        
        self.session.add(data_source)
        self.session.commit()
        return data_source
    
    def get_lead_data_sources(self, lead_id: int) -> List[LeadDataSource]:
        """
        Get all data sources for a lead.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            List of LeadDataSource objects
        """
        return self.session.query(LeadDataSource)\
            .filter(LeadDataSource.lead_id == lead_id)\
            .order_by(desc(LeadDataSource.data_timestamp))\
            .all()
    
    def add_tag_to_lead(self, lead_id: int, tag_name: str, color: str = None) -> Tag:
        """
        Add a tag to a lead. Create the tag if it doesn't exist.
        
        Args:
            lead_id: ID of the lead
            tag_name: Name of the tag
            color: Hex color code (optional)
            
        Returns:
            The Tag object
        """
        lead = self.session.query(Lead).get(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
            
        # Find or create the tag
        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, color=color or "#CCCCCC")
            self.session.add(tag)
            self.session.commit()
            
        # Add tag to lead if not already added
        if tag not in lead.tags:
            lead.tags.append(tag)
            self.session.commit()
            
        return tag
    
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
            generated_at=datetime.fromisoformat(email_data['generated_at']) if isinstance(email_data['generated_at'], str) else email_data['generated_at']
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
        lead.updated_at = datetime.utcnow()
        
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
    
    def get_lead_statistics(self):
        """Get statistics about leads in the database."""
        total_leads = self.session.query(func.count(Lead.id)).scalar()
        
        # Leads by status
        status_counts = self.session.query(
            Lead.status, 
            func.count(Lead.id)
        ).group_by(Lead.status).all()
        
        # Leads by source
        source_counts = self.session.query(
            Lead.source, 
            func.count(Lead.id)
        ).group_by(Lead.source).all()
        
        # Leads with email/phone
        with_email = self.session.query(func.count(Lead.id))\
            .filter(Lead.email != None, Lead.email != '')\
            .scalar()
            
        with_phone = self.session.query(func.count(Lead.id))\
            .filter(Lead.phone != None, Lead.phone != '')\
            .scalar()
            
        # Average completeness score
        avg_score = self.session.query(func.avg(Lead.completeness_score)).scalar() or 0
        
        return {
            'total_leads': total_leads,
            'status_counts': {status.name: count for status, count in status_counts},
            'source_counts': {source.name: count for source, count in source_counts},
            'with_email': with_email,
            'with_phone': with_phone,
            'average_completeness': round(float(avg_score), 2)
        } 