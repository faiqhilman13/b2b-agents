#!/usr/bin/env python3
"""
Database Migration Script for Malaysian Lead Generator.

This script migrates data from the old database schema to the new enhanced schema
that supports rich data from MCP-powered Apify Actors.

Usage:
    python migrate_database.py [--db-path=path/to/database.db] [--backup]
"""

import os
import sys
import argparse
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to import the lead_generator package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lead_generator.database.models import (
    init_db, 
    Base, 
    Lead, 
    EmailGeneration, 
    LeadStatusHistory,
    LeadStatus,
    DataSource,
    Location,
    BusinessDetail,
    SocialMediaProfile,
    LeadDataSource
)
from lead_generator.utils.data_processor import _calculate_completeness_score, _parse_address
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

def backup_database(db_path):
    """Create a backup of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"Created backup at {backup_path}")
    return backup_path

def check_old_schema(engine):
    """Check if the database has the old schema."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("Database is empty. No migration needed.")
        return False
    
    lead_columns = {col['name'] for col in inspector.get_columns('leads')} if 'leads' in tables else set()
    
    # Check if we have the old schema (no alternative_emails, no website, etc.)
    is_old_schema = ('leads' in tables and 
                    'alternative_emails' not in lead_columns and
                    'website' not in lead_columns and
                    'industry' not in lead_columns)
    
    if not is_old_schema:
        print("Database already has the new schema or is in an unknown state.")
        return False
    
    return True

def migrate_leads(session, conn):
    """Migrate leads from old schema to new schema."""
    # Get existing leads from old schema
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, organization, person_name, role, email, phone, source_url, status, created_at, updated_at
        FROM leads
    ''')
    
    old_leads = cursor.fetchall()
    print(f"Found {len(old_leads)} leads to migrate")
    
    # Map old status names to new enum values
    status_mapping = {
        'new': LeadStatus.NEW,
        'contacted': LeadStatus.CONTACTED,
        'responded': LeadStatus.RESPONDED,
        'qualified': LeadStatus.QUALIFIED,
        'disqualified': LeadStatus.DISQUALIFIED,
        'booked': LeadStatus.BOOKED,
        'closed': LeadStatus.CLOSED,
        'ghosted': LeadStatus.GHOSTED
    }
    
    for old_lead in old_leads:
        lead_id, org, name, role, email, phone, source_url, status, created_at, updated_at = old_lead
        
        # Extract website from source_url if it exists
        website = source_url if (source_url and source_url.startswith('http')) else None
        
        # Parse address if available in organization field (some legacy data stored it there)
        address_parts = {}
        if ',' in org:
            address_parts = _parse_address(org)
            # If we found address parts, clean the organization name
            if address_parts.get('city'):
                org = org.split(',')[0].strip()
        
        # Create new lead object with enhanced schema
        lead = Lead(
            id=lead_id,  # Preserve original ID
            organization=org,
            person_name=name,
            role=role,
            email=email,
            phone=phone,
            website=website,
            source_url=source_url,
            source=DataSource.MANUAL,  # Default for legacy data
            status=status_mapping.get(status, LeadStatus.NEW) if status else LeadStatus.NEW,
            created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
            updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow()
        )
        
        # Calculate completeness score
        lead_data = {
            'organization': org,
            'person_name': name,
            'role': role,
            'email': email,
            'phone': phone,
            'website': website
        }
        lead.completeness_score = _calculate_completeness_score(lead_data)
        
        # Add to session but don't commit yet
        session.add(lead)
        
        # Create location if we have address parts
        if address_parts.get('city') or address_parts.get('street'):
            location = Location(
                lead_id=lead_id,
                address=address_parts.get('street', ''),
                city=address_parts.get('city', ''),
                state=address_parts.get('state', ''),
                postal_code=address_parts.get('postal_code', ''),
                is_primary=True
            )
            session.add(location)
    
    # Commit all leads and locations at once
    session.commit()
    print("Migrated leads and created locations where possible")

def migrate_email_generations(session, conn):
    """Migrate email generations from old schema to new schema."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, lead_id, template_name, subject, body, generated_at, sent_at, response_received
        FROM email_generations
    ''')
    
    old_generations = cursor.fetchall()
    print(f"Found {len(old_generations)} email generations to migrate")
    
    for old_gen in old_generations:
        gen_id, lead_id, template, subject, body, generated_at, sent_at, response_received = old_gen
        
        # Create new email generation
        generation = EmailGeneration(
            id=gen_id,  # Preserve original ID
            lead_id=lead_id,
            template_name=template,
            subject=subject,
            body=body,
            generated_at=datetime.fromisoformat(generated_at) if generated_at else datetime.utcnow(),
            sent_at=datetime.fromisoformat(sent_at) if sent_at else None,
            response_received=datetime.fromisoformat(response_received) if response_received else None
        )
        
        session.add(generation)
    
    session.commit()
    print("Migrated email generations")

def migrate_status_history(session, conn):
    """Migrate lead status history from old schema to new schema."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, lead_id, old_status, new_status, changed_at, notes
        FROM lead_status_history
    ''')
    
    old_history = cursor.fetchall()
    print(f"Found {len(old_history)} status history entries to migrate")
    
    # Map old status names to new enum values
    status_mapping = {
        'new': LeadStatus.NEW,
        'contacted': LeadStatus.CONTACTED,
        'responded': LeadStatus.RESPONDED,
        'qualified': LeadStatus.QUALIFIED,
        'disqualified': LeadStatus.DISQUALIFIED,
        'booked': LeadStatus.BOOKED,
        'closed': LeadStatus.CLOSED,
        'ghosted': LeadStatus.GHOSTED
    }
    
    for old_entry in old_history:
        entry_id, lead_id, old_status, new_status, changed_at, notes = old_entry
        
        # Create new status history entry
        history = LeadStatusHistory(
            id=entry_id,  # Preserve original ID
            lead_id=lead_id,
            old_status=status_mapping.get(old_status, None) if old_status else None,
            new_status=status_mapping.get(new_status, LeadStatus.NEW) if new_status else LeadStatus.NEW,
            changed_at=datetime.fromisoformat(changed_at) if changed_at else datetime.utcnow(),
            notes=notes
        )
        
        session.add(history)
    
    session.commit()
    print("Migrated status history")

def add_data_sources(session):
    """Add data source entries for all leads to track origin."""
    leads = session.query(Lead).all()
    print(f"Adding data source entries for {len(leads)} leads")
    
    for lead in leads:
        # Create a data source entry to indicate this is migrated data
        data_source = LeadDataSource(
            lead_id=lead.id,
            source_type=lead.source,
            source_url=lead.source_url,
            data_timestamp=lead.created_at
        )
        
        session.add(data_source)
    
    session.commit()
    print("Added data source entries")

def detect_and_add_social_media(session):
    """Detect potential social media links in source URLs and add as profiles."""
    leads = session.query(Lead).all()
    
    social_platforms = {
        'instagram.com': 'instagram',
        'facebook.com': 'facebook',
        'linkedin.com': 'linkedin',
        'twitter.com': 'twitter',
        'youtube.com': 'youtube'
    }
    
    profile_count = 0
    
    for lead in leads:
        if not lead.source_url:
            continue
            
        url = lead.source_url.lower()
        
        for platform_url, platform_name in social_platforms.items():
            if platform_url in url:
                # Create social media profile
                profile = SocialMediaProfile(
                    platform=platform_name,
                    url=lead.source_url,
                    last_updated=datetime.utcnow()
                )
                
                lead.social_media_profiles.append(profile)
                profile_count += 1
                break
    
    if profile_count > 0:
        session.commit()
        print(f"Added {profile_count} detected social media profiles")
    else:
        print("No social media profiles detected in source URLs")

def migrate_database(db_path, backup):
    """
    Migrate the database from old schema to new schema.
    
    Args:
        db_path: Path to the SQLite database file
        backup: Whether to create a backup before migration
    """
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    # Create backup if requested
    if backup:
        backup_path = backup_database(db_path)
    
    # Create SQLAlchemy engine and check schema
    engine = create_engine(f"sqlite:///{db_path}")
    
    if not check_old_schema(engine):
        return False
    
    # Create new tables
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Direct SQLite connection for reading old data
    conn = sqlite3.connect(db_path)
    
    try:
        # Perform migration steps
        migrate_leads(session, conn)
        migrate_email_generations(session, conn)
        migrate_status_history(session, conn)
        add_data_sources(session)
        detect_and_add_social_media(session)
        
        print("Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        session.rollback()
        
        if backup:
            print(f"You can restore from the backup at {backup_path}")
        
        return False
    
    finally:
        session.close()
        conn.close()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate Malaysian Lead Generator database to new schema")
    parser.add_argument("--db-path", default="lead_generator.db", help="Path to the SQLite database file")
    parser.add_argument("--backup", action="store_true", help="Create a backup before migration")
    
    args = parser.parse_args()
    
    success = migrate_database(args.db_path, args.backup)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 