#!/usr/bin/env python3
"""
Database models for the lead generator.

This module defines the SQLite schema for storing:
- Leads
- Email generations
- Lead status
- Generation history
- Dashboard statistics
- Social media profiles
- Location data
- Data source tracking
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Date, Float, Boolean, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import enum

Base = declarative_base()

# Association table for many-to-many relationship between leads and social media profiles
lead_social_media_association = Table(
    'lead_social_media',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey('leads.id'), primary_key=True),
    Column('social_media_id', Integer, ForeignKey('social_media_profiles.id'), primary_key=True)
)

# Association table for many-to-many relationship between leads and tags
lead_tag_association = Table(
    'lead_tags',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey('leads.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class LeadStatus(enum.Enum):
    """Enumeration of possible lead statuses."""
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    BOOKED = "booked"
    CLOSED = "closed"
    GHOSTED = "ghosted"

class DataSource(enum.Enum):
    """Enumeration of possible data sources."""
    GOOGLE_MAPS = "google_maps"
    INSTAGRAM = "instagram"
    WEB_BROWSER = "web_browser"
    MANUAL = "manual"
    IMPORTED = "imported"
    OTHER = "other"

class Tag(Base):
    """Model for storing tags that can be applied to leads."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), default="#CCCCCC")
    created_at = Column(DateTime, default=datetime.utcnow)

class SocialMediaProfile(Base):
    """Model for storing social media profile information."""
    __tablename__ = 'social_media_profiles'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # e.g., instagram, facebook, linkedin
    url = Column(String(512), nullable=False)
    username = Column(String(255))
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to leads
    leads = relationship("Lead", secondary=lead_social_media_association, back_populates="social_media_profiles")

class Location(Base):
    """Model for storing location information."""
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    address = Column(String(512))
    street = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Malaysia")
    latitude = Column(Float)
    longitude = Column(Float)
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to lead
    lead = relationship("Lead", back_populates="locations")

class BusinessDetail(Base):
    """Model for storing detailed business information."""
    __tablename__ = 'business_details'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), unique=True)
    rating = Column(Float)
    reviews_count = Column(Integer, default=0)
    price_level = Column(Integer)
    category = Column(String(255))
    subcategories = Column(String(512))  # Comma-separated list
    year_established = Column(Integer)
    employee_count = Column(String(50))
    services = Column(Text)
    products = Column(Text)
    business_hours = Column(Text)  # JSON string of business hours
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to lead
    lead = relationship("Lead", back_populates="business_detail")

class Lead(Base):
    """Model for storing lead information."""
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    organization = Column(String(255), nullable=False)
    person_name = Column(String(255))
    role = Column(String(255))
    email = Column(String(255))
    alternative_emails = Column(String(512))  # Comma-separated list of additional emails
    phone = Column(String(50))
    alternative_phones = Column(String(255))  # Comma-separated list of additional phones
    website = Column(String(512))
    industry = Column(String(255))
    source = Column(Enum(DataSource), default=DataSource.MANUAL)
    source_url = Column(String(512))
    notes = Column(Text)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    completeness_score = Column(Float, default=0.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email_generations = relationship("EmailGeneration", back_populates="lead")
    status_history = relationship("LeadStatusHistory", back_populates="lead")
    social_media_profiles = relationship("SocialMediaProfile", secondary=lead_social_media_association, back_populates="leads")
    locations = relationship("Location", back_populates="lead")
    business_detail = relationship("BusinessDetail", uselist=False, back_populates="lead")
    data_sources = relationship("LeadDataSource", back_populates="lead")
    tags = relationship("Tag", secondary=lead_tag_association)

class EmailGeneration(Base):
    """Model for storing generated emails."""
    __tablename__ = 'email_generations'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    template_name = Column(String(255), nullable=False)
    subject = Column(String(512), nullable=False)
    body = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    response_received = Column(DateTime, nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="email_generations")

class LeadStatusHistory(Base):
    """Model for tracking lead status changes."""
    __tablename__ = 'lead_status_history'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    old_status = Column(Enum(LeadStatus))
    new_status = Column(Enum(LeadStatus), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="status_history")

class LeadDataSource(Base):
    """Model for tracking where lead data came from."""
    __tablename__ = 'lead_data_sources'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    source_type = Column(Enum(DataSource), nullable=False)
    source_url = Column(String(512))
    raw_data = Column(Text)  # JSON string of the raw data
    data_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="data_sources")

class DashboardStats(Base):
    """Model for storing dashboard statistics."""
    __tablename__ = 'dashboard_stats'
    
    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, default=date.today)
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    meetings_booked = Column(Integer, default=0)
    data_json = Column(Text)  # Detailed statistics as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(db_path: str = "lead_generator.db"):
    """Initialize the database and create tables."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine 