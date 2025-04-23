#!/usr/bin/env python3
"""
Database models for the lead generator.

This module defines the SQLite schema for storing:
- Leads
- Email generations
- Lead status
- Generation history
- Dashboard statistics
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

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

class Lead(Base):
    """Model for storing lead information."""
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    organization = Column(String(255), nullable=False)
    person_name = Column(String(255))
    role = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    source_url = Column(String(512))
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email_generations = relationship("EmailGeneration", back_populates="lead")
    status_history = relationship("LeadStatusHistory", back_populates="lead")

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