#!/usr/bin/env python3
"""
Lead Generator - Malaysian Business Contact Collection Tool

This tool helps collect business leads from various Malaysian sources including:
- Google Maps (MCP-powered Apify Actor)
- Instagram (MCP-powered Apify Actor)
- Web Browser (MCP-powered Apify Actor)
- Yellow Pages Malaysia
- Government ministry websites
- University staff directories

It also provides functionality to generate and send personalized emails to collected leads.

Run this script with the appropriate arguments to start collecting leads.
"""

import argparse
import logging
import os
import sys
import time
import csv
import glob
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Make sure we can import from the current directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from lead_generator.agents.yellow_pages_scraper import YellowPagesScraper
from lead_generator.agents.gov_ministry_scraper import GovMinistryScraper
from lead_generator.agents.university_scraper import UniversityScraper
from lead_generator.agents.email_generator import EmailGenerator
from lead_generator.agents.email_sender import EmailSender, email_sender
from lead_generator.utils.email_validator import EmailValidator
from lead_generator.utils.cache import EmailCache
from lead_generator.utils.data_processor import (
    standardize_lead, 
    enrich_lead, 
    deduplicate_leads, 
    filter_leads_by_completeness
)
from lead_generator.database.models import init_db, Lead, LeadStatus
from lead_generator.database.queries import LeadQueries
from sqlalchemy.orm import sessionmaker
from lead_generator.config.email_config import EMAIL_VALIDATION
from lead_generator.config.proposal_config import get_package_pdf, list_available_packages

# Import MCP-powered API clients
from lead_generator.agents.api_clients import (
    activate_clients,
    get_client,
    GoogleMapsClient,
    InstagramClient,
    WebBrowserClient
)

# Set up logging
def setup_logging(log_level="INFO"):
    """Set up logging configuration."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"lead_generator_{timestamp}.log")
    
    level = getattr(logging, log_level.upper())
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("lead_generator")

# MCP-Powered Data Sources Settings
GOOGLE_MAPS_CATEGORIES = [
    "software development",
    "engineering consulting",
    "training center",
    "marketing agency",
    "event management",
    "financial services",
    "education center",
    "consulting firm"
]

GOOGLE_MAPS_LOCATIONS = [
    "Kuala Lumpur",
    "Petaling Jaya",
    "Penang",
    "Johor Bahru",
    "Shah Alam",
    "Cyberjaya",
    "Puchong",
    "Bandar Sunway"
]

INSTAGRAM_BUSINESS_TAGS = [
    "malaysiatech",
    "malaysiabusiness",
    "klentrepreneur",
    "mbbiz",
    "kualalumpurbusiness",
    "malaysiastartup",
    "malaysiaconsulting"
]

WEB_SEARCH_QUERIES = [
    "top software companies in Malaysia",
    "engineering consulting firms Kuala Lumpur",
    "business training Malaysia",
    "financial advisory services Petaling Jaya",
    "education consulting Malaysia",
    "executive training programs Kuala Lumpur"
]

# Yellow Pages Categories of interest
# These categories work with Yellow Pages Malaysia (yellowpages.my)
YELLOW_PAGES_CATEGORIES = [
    "education",
    "engineering",
    "training",
    "hotels",
    "consultants",
    "advertising",
    "marketing",
    "financial-services"
]

# BusinessList.my categories (used as an alternative to Yellow Pages)
BUSINESS_LIST_CATEGORIES = [
    "training",
    "engineering",
    "hotels",
    "education",
    "event-management",
    "advertising",
    "marketing",
    "consultants"
]

# Government ministry websites
GOVERNMENT_WEBSITES = [
    "https://www.kpkt.gov.my",    # Ministry of Housing and Local Government
    "https://www.moh.gov.my",     # Ministry of Health
    "https://www.miti.gov.my",    # Ministry of International Trade and Industry
    "https://www.mof.gov.my",     # Ministry of Finance
    "https://www.mdec.my",        # Malaysia Digital Economy Corporation
    "https://www.jpj.gov.my",     # Road Transport Department
    "https://www.jpa.gov.my"      # Public Service Department
]

# University websites
UNIVERSITY_WEBSITES = [
    "https://www.um.edu.my",      # University of Malaya
    "https://www.usm.my",         # Universiti Sains Malaysia
    "https://www.utm.my",         # Universiti Teknologi Malaysia
    "https://www.upm.edu.my",     # Universiti Putra Malaysia
    "https://www.ukm.my",         # Universiti Kebangsaan Malaysia
    "https://www.utp.edu.my",     # Universiti Teknologi PETRONAS
    "https://www.mmu.edu.my",     # Multimedia University
    "https://www.uitm.edu.my"     # Universiti Teknologi MARA
]

def run_yellow_pages_scraper(args, logger):
    """Run the Yellow Pages scraper with specified arguments."""
    logger.info("Starting Yellow Pages Malaysia scraper")
    
    # Initialize the scraper
    output_file = args.output_dir + "/yellow_pages_leads.csv"
    
    # Select the appropriate directory site
    if args.use_businesslist:
        base_url = "https://www.businesslist.my"
        default_categories = BUSINESS_LIST_CATEGORIES
        logger.info("Using BusinessList.my as the directory source")
    else:
        base_url = "https://www.yellowpages.my"
        default_categories = YELLOW_PAGES_CATEGORIES
        logger.info("Using YellowPages.my as the directory source")
        
    scraper = YellowPagesScraper(base_url=base_url, output_file=output_file)
    
    # Use provided categories or default list
    categories = args.yp_categories.split(",") if args.yp_categories else default_categories
    
    # Limit the number of categories if specified
    if args.limit_sources and len(categories) > args.limit_sources:
        categories = categories[:args.limit_sources]
        
    logger.info(f"Scraping {len(categories)} categories: {', '.join(categories)}")
    
    # Run the scraper
    total_leads = scraper.scrape_multiple_categories(
        categories=categories,
        max_pages_per_category=args.max_pages_per_source,
        delay_between_categories=(args.min_delay, args.max_delay)
    )
    
    logger.info(f"Yellow Pages scraper completed. Total leads collected: {total_leads}")
    return total_leads

def run_gov_ministry_scraper(args, logger):
    """Run the Government Ministry scraper with specified arguments."""
    logger.info("Starting Government Ministry scraper")
    
    # Initialize the scraper
    output_file = args.output_dir + "/gov_ministry_leads.csv"
    scraper = GovMinistryScraper(output_file=output_file)
    
    # Use provided websites or default list
    websites = args.gov_websites.split(",") if args.gov_websites else GOVERNMENT_WEBSITES
    
    # Limit the number of websites if specified
    if args.limit_sources and len(websites) > args.limit_sources:
        websites = websites[:args.limit_sources]
        
    logger.info(f"Scraping {len(websites)} government websites: {', '.join(websites)}")
    
    # Run the scraper
    total_leads = scraper.scrape_multiple_ministries(
        ministry_urls=websites,
        max_pages_per_ministry=args.max_pages_per_source,
        delay_between_ministries=(args.min_delay, args.max_delay)
    )
    
    logger.info(f"Government Ministry scraper completed. Total leads collected: {total_leads}")
    return total_leads

def run_university_scraper(args, logger):
    """Run the University scraper with specified arguments."""
    logger.info("Starting University staff directory scraper")
    
    # Initialize the scraper
    output_file = args.output_dir + "/university_leads.csv"
    scraper = UniversityScraper(output_file=output_file)
    
    # Use provided websites or default list
    websites = args.uni_websites.split(",") if args.uni_websites else UNIVERSITY_WEBSITES
    
    # Limit the number of websites if specified
    if args.limit_sources and len(websites) > args.limit_sources:
        websites = websites[:args.limit_sources]
        
    logger.info(f"Scraping {len(websites)} university websites: {', '.join(websites)}")
    
    # Run the scraper
    total_leads = scraper.scrape_multiple_universities(
        university_urls=websites,
        max_pages_per_university=args.max_pages_per_source,
        delay_between_universities=(args.min_delay, args.max_delay)
    )
    
    logger.info(f"University scraper completed. Total leads collected: {total_leads}")
    return total_leads

def combine_csv_files(output_dir, output_file, logger):
    """Combine all CSV files in the output directory into a single file."""
    logger.info(f"Combining CSV files into {output_file}")
    
    # Get all CSV files
    csv_files = glob.glob(f"{output_dir}/*_leads.csv")
    
    if not csv_files:
        logger.warning("No CSV files found to combine")
        return
    
    # Get the header from the first file
    with open(csv_files[0], 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
    
    # Create the combined file with header
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        
        # Process each file
        for file in csv_files:
            with open(file, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                next(reader)  # Skip header
                for row in reader:
                    writer.writerow(row)
    
    logger.info(f"Successfully combined {len(csv_files)} CSV files into {output_file}")
    return output_file

def import_leads_to_database(input_file, logger):
    """Import leads from JSON or CSV file to database."""
    logger.info(f"Importing leads from {input_file} to database")
    
    # Initialize database
    db_path = "leads.db"
    engine = init_db(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    queries = LeadQueries(session)
    
    # Import leads
    total_imported = 0
    total_skipped = 0
    
    try:
        # Load leads from file
        leads = []
        
        if input_file.endswith('.json'):
            # JSON file format
            with open(input_file, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        else:
            # CSV file format
            with open(input_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                leads = list(reader)
        
        logger.info(f"Loaded {len(leads)} leads from {input_file}")
        
        # Process each lead
        for lead in leads:
            # Check if email is valid
            if not lead.get('email'):
                logger.debug(f"Skipping lead without email: {lead.get('organization', 'Unknown')}")
                total_skipped += 1
                continue
                
            email_valid, _ = EmailValidator.validate_email(lead.get('email'))
            if not email_valid:
                logger.debug(f"Skipping lead with invalid email: {lead.get('email')}")
                total_skipped += 1
                continue
                
            # Check if lead already exists
            existing_lead = queries.get_lead(email=lead.get('email'))
            if existing_lead:
                logger.debug(f"Lead already exists: {lead.get('email')}")
                total_skipped += 1
                continue
            
            # Extract lead data from the standardized format
            lead_data = {
                'organization': lead.get('organization', ''),
                'person_name': lead.get('person_name', ''),
                'role': lead.get('role', ''),
                'email': lead.get('email', ''),
                'phone': lead.get('phone', ''),
                'website': lead.get('website', ''),
                'industry': lead.get('industry', ''),
                'source_url': lead.get('source_url', '')
            }
            
            # Add enhanced data if available
            if 'address' in lead or 'city' in lead:
                # Location data
                location_data = {
                    'address': lead.get('address', ''),
                    'city': lead.get('city', ''),
                    'state': lead.get('state', ''),
                    'postal_code': lead.get('postal_code', ''),
                    'latitude': lead.get('location', {}).get('latitude'),
                    'longitude': lead.get('location', {}).get('longitude')
                }
                
                # Add location to lead_data for reference
                lead_data['location_data'] = location_data
            
            # Add business details if available
            if 'rating' in lead or 'reviews_count' in lead:
                # Business details
                business_details = {
                    'rating': lead.get('rating'),
                    'reviews_count': lead.get('reviews_count', 0),
                    'category': lead.get('industry', '')
                }
                
                # Add business details to lead_data for reference
                lead_data['business_details'] = business_details
            
            # Add social media profiles if available
            if 'social_media' in lead and isinstance(lead['social_media'], dict):
                # Social media profiles
                social_media = []
                
                for platform, url in lead['social_media'].items():
                    if url:
                        social_media.append({
                            'platform': platform,
                            'url': url
                        })
                
                # Add social media to lead_data for reference
                lead_data['social_media'] = social_media
            
            # Save lead to database
            saved_lead = queries.save_lead(lead_data)
            total_imported += 1
            
            # Now add related data if it was included
            if saved_lead and hasattr(saved_lead, 'id'):
                # Add location data
                if 'location_data' in lead_data and any(lead_data['location_data'].values()):
                    try:
                        queries.add_lead_location(saved_lead.id, lead_data['location_data'])
                    except Exception as e:
                        logger.error(f"Error adding location data: {str(e)}")
                
                # Add business details
                if 'business_details' in lead_data and any(lead_data['business_details'].values()):
                    try:
                        queries.add_business_details(saved_lead.id, lead_data['business_details'])
                    except Exception as e:
                        logger.error(f"Error adding business details: {str(e)}")
                
                # Add social media profiles
                if 'social_media' in lead_data and lead_data['social_media']:
                    for profile in lead_data['social_media']:
                        try:
                            queries.add_social_media_profile(
                                saved_lead.id,
                                platform=profile['platform'],
                                url=profile['url']
                            )
                        except Exception as e:
                            logger.error(f"Error adding social media profile: {str(e)}")
                
                # Add data source
                if 'source' in lead:
                    try:
                        # Convert string source to DataSource enum
                        source_type = lead.get('source', '').upper()
                        if source_type in [s.name for s in DataSource]:
                            source = DataSource[source_type]
                            queries.add_lead_data_source(
                                saved_lead.id,
                                source_type=source,
                                source_url=lead.get('source_url', ''),
                                raw_data=lead.get('metadata', {})
                            )
                    except Exception as e:
                        logger.error(f"Error adding data source: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error importing leads: {str(e)}")
        session.rollback()
    finally:
        session.close()
    
    logger.info(f"Lead import completed. Imported: {total_imported}, Skipped: {total_skipped}")
    return total_imported

def generate_emails(args, logger):
    """Generate emails for leads in database."""
    logger.info("Starting email generation")
    
    # Initialize database and email generator
    db_path = "leads.db"
    engine = init_db(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    queries = LeadQueries(session)
    
    email_generator = EmailGenerator()
    email_cache = EmailCache()
    
    # Get leads with specified status
    status = LeadStatus.NEW
    if args.lead_status:
        status = LeadStatus[args.lead_status.upper()]
    
    leads = queries.get_leads_by_status(status)
    logger.info(f"Found {len(leads)} leads with status: {status.value}")
    
    # Select appropriate template based on source
    template_map = {
        'yellowpages': 'default',
        'businesslist': 'default',
        'gov': 'government',
        'university': 'university'
    }
    
    # Template override if specified
    template_override = args.email_template
    
    # Generate emails
    generated_emails = []
    total_generated = 0
    
    for lead in leads:
        # Determine template
        source = lead.source_url or ""
        template_name = template_override
        
        if not template_name:
            if 'gov.my' in source:
                template_name = template_map['gov']
            elif 'edu.my' in source:
                template_name = template_map['university']
            else:
                template_name = template_map['businesslist']
        
        # Convert DB model to dict
        lead_dict = {
            'organization': lead.organization,
            'person_name': lead.person_name,
            'role': lead.role,
            'email': lead.email,
            'phone': lead.phone,
            'source_url': lead.source_url
        }
        
        # Check if email can be generated (not in cache)
        if not args.force_generation and not email_cache.can_generate(lead_dict, template_name):
            logger.debug(f"Skipping email generation for {lead.email} (recently generated)")
            continue
        
        # Generate email
        try:
            email_data = email_generator.generate_email(lead_dict, template_name)
            
            # Save to database
            queries.save_email_generation(lead.id, email_data)
            
            # Record in cache
            email_cache.record_generation(lead_dict, template_name, email_data)
            
            # Add to list for sending
            if args.send_emails:
                generated_emails.append(email_data)
                
            total_generated += 1
            
            # Update lead status if needed
            if args.update_status:
                queries.update_lead_status(lead.id, LeadStatus.CONTACTED, 
                                          f"Email generated with template: {template_name}")
                
            logger.debug(f"Generated email for {lead.email} using template: {template_name}")
            
            # Save to file if requested
            if args.email_output_dir:
                os.makedirs(args.email_output_dir, exist_ok=True)
                email_file = os.path.join(args.email_output_dir, f"{lead.id}_{template_name}.txt")
                
                with open(email_file, 'w', encoding='utf-8') as f:
                    f.write(f"Subject: {email_data['subject']}\n\n")
                    f.write(email_data['body'])
                    
        except Exception as e:
            logger.error(f"Error generating email for {lead.email}: {str(e)}")
    
    session.close()
    
    logger.info(f"Email generation completed. Total generated: {total_generated}")
    return generated_emails

def send_emails(emails, args, logger):
    """Send generated emails."""
    if not emails:
        logger.info("No emails to send")
        return 0
        
    logger.info(f"Starting email sending for {len(emails)} emails")
    
    # Check for dry run
    if args.dry_run:
        logger.info("Dry run enabled - emails will not be sent")
        for email in emails:
            logger.info(f"Would send email to: {email['to_email']}, Subject: {email['subject']}")
        return 0
    
    # Initialize email sender
    smtp_config = {
        'smtp_server': args.smtp_server,
        'smtp_port': args.smtp_port,
        'username': args.smtp_username,
        'password': args.smtp_password,
        'from_email': args.from_email,
        'from_name': args.from_name,
        'rate_limit': args.email_rate_limit,
        'batch_size': args.email_batch_size
    }
    
    # Handle PDF proposal attachments - priority order:
    # 1. Explicit file attachment via --attach-proposal
    # 2. Package-based selection if --use-package-selection is set
    # 3. Directory-based selection via --proposal-dir
    
    # Check for explicit proposal attachment
    attachment_paths = None
    if args.attach_proposal:
        # Check if the file exists
        if os.path.isfile(args.attach_proposal):
            attachment_paths = args.attach_proposal
            logger.info(f"Will attach proposal: {args.attach_proposal}")
        else:
            logger.warning(f"Proposal file not found: {args.attach_proposal}")
    
    # Get available packages for logging
    if args.use_package_selection:
        available_packages = list_available_packages()
        if available_packages:
            logger.info(f"Found {len(available_packages)} available package types:")
            for pkg in available_packages:
                logger.info(f"  - {pkg['type']}: {pkg['description']}")
                if pkg['variants']:
                    logger.info(f"    Variants: {', '.join(pkg['variants'].keys())}")
        else:
            logger.warning("No package PDFs found in the proposals directory. Package-based selection will not work.")
    
    # Handle proposal directory
    proposal_files = []
    if args.proposal_dir and not attachment_paths and not args.use_package_selection:
        if os.path.isdir(args.proposal_dir):
            # Get all PDF files in the directory
            for file in os.listdir(args.proposal_dir):
                if file.lower().endswith('.pdf'):
                    proposal_files.append(os.path.join(args.proposal_dir, file))
            
            if proposal_files:
                logger.info(f"Found {len(proposal_files)} proposal files in {args.proposal_dir}")
            else:
                logger.warning(f"No PDF files found in directory: {args.proposal_dir}")
        else:
            logger.warning(f"Proposal directory not found: {args.proposal_dir}")
    
    # Enrich emails with attachment information
    for email in emails:
        # Get the lead data from the email
        lead_data = {
            "organization": email.get("organization", ""),
            "person_name": email.get("person_name", ""),
            "role": email.get("role", ""),
            "email": email.get("to_email", ""),
            # Extract any other fields we might have
            "source_url": email.get("source_url", ""),
            "notes": email.get("notes", "")
        }
        
        # Use a single file if specified
        if attachment_paths:
            email['attachment_paths'] = attachment_paths
        # Use package-based selection if enabled
        elif args.use_package_selection:
            # Get the template name from the email if available
            template_name = email.get("template_used", "default")
            package_pdf = get_package_pdf(lead_data, template_name)
            if package_pdf:
                email['attachment_paths'] = package_pdf
                logger.info(f"Selected package PDF for {lead_data['organization']}: {os.path.basename(package_pdf)} (based on template: {template_name})")
            else:
                logger.warning(f"No suitable package found for {lead_data['organization']}")
        # Otherwise select a proposal based on simple criteria
        elif proposal_files:
            # For now, let's just use the first one, but we'll log this
            email['attachment_paths'] = proposal_files[0]
            logger.info(f"Using basic proposal selection for {lead_data['organization']}: {os.path.basename(proposal_files[0])}")
    
    # Send emails
    try:
        with email_sender(smtp_config) as sender:
            results = sender.send_batch(emails, max_retries=3)
            
            logger.info(f"Email sending completed. Success: {results['success']}, Failure: {results['failure']}")
            return results['success']
    except Exception as e:
        logger.error(f"Error sending emails: {str(e)}")
        return 0

def run_google_maps_client(args, logger):
    """Run the Google Maps client to collect business data."""
    logger.info("Starting Google Maps data collection")
    
    # Get the Google Maps client
    try:
        gmaps_client = get_client('google_maps')
        if not gmaps_client:
            logger.error("Failed to initialize Google Maps client. Check your API configuration.")
            return 0
    except Exception as e:
        logger.error(f"Error initializing Google Maps client: {str(e)}")
        return 0
    
    # Determine the search parameters
    if args.search:
        query = args.search
        logger.info(f"Searching for businesses using query: {query}")
    else:
        # Default to categories if no search query
        categories = args.categories.split(",") if args.categories else GOOGLE_MAPS_CATEGORIES
        if args.limit_sources and len(categories) > args.limit_sources:
            categories = categories[:args.limit_sources]
        
        query = categories[0]  # Use the first category as query
        logger.info(f"Searching for businesses in category: {query}")
    
    # Determine location
    location = args.location
    if not location:
        # Use the first location from defaults
        location = GOOGLE_MAPS_LOCATIONS[0]
    
    logger.info(f"Using location: {location}")
    
    # Determine result limit
    limit = args.limit if args.limit else 20
    logger.info(f"Limiting results to: {limit}")
    
    # Set up output file
    output_file = os.path.join(args.output_dir, "google_maps_leads.json")
    
    try:
        # Search for businesses
        businesses = gmaps_client.search_businesses(
            query=query,
            location=location,
            limit=limit
        )
        
        if not businesses:
            logger.warning("No businesses found from Google Maps search")
            return 0
        
        logger.info(f"Found {len(businesses)} businesses from Google Maps")
        
        # Standardize the data
        standardized_leads = []
        for business in businesses:
            try:
                lead = standardize_lead(business, "google_maps")
                standardized_leads.append(lead)
            except Exception as e:
                logger.error(f"Error standardizing lead data: {str(e)}")
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_leads, f, indent=2)
        
        logger.info(f"Saved {len(standardized_leads)} standardized leads to {output_file}")
        
        # Save to CSV for backward compatibility
        csv_output_file = os.path.join(args.output_dir, "google_maps_leads.csv")
        _convert_leads_to_csv(standardized_leads, csv_output_file)
        logger.info(f"Saved leads to CSV for compatibility: {csv_output_file}")
        
        return len(standardized_leads)
        
    except Exception as e:
        logger.error(f"Error in Google Maps client: {str(e)}")
        return 0

def run_instagram_client(args, logger):
    """Run the Instagram client to collect business data."""
    logger.info("Starting Instagram data collection")
    
    # Get the Instagram client
    try:
        instagram_client = get_client('instagram')
        if not instagram_client:
            logger.error("Failed to initialize Instagram client. Check your API configuration.")
            return 0
    except Exception as e:
        logger.error(f"Error initializing Instagram client: {str(e)}")
        return 0
    
    # Determine the search parameters
    if args.search:
        query = args.search
        logger.info(f"Searching Instagram using query: {query}")
    else:
        # Default to hashtags if no search query
        hashtags = args.hashtags.split(",") if args.hashtags else INSTAGRAM_BUSINESS_TAGS
        if args.limit_sources and len(hashtags) > args.limit_sources:
            hashtags = hashtags[:args.limit_sources]
        
        # Add # if not present
        query = hashtags[0] if hashtags[0].startswith("#") else f"#{hashtags[0]}"
        logger.info(f"Searching Instagram with hashtag: {query}")
    
    # Determine result limit
    limit = args.limit if args.limit else 20
    logger.info(f"Limiting results to: {limit}")
    
    # Set up output file
    output_file = os.path.join(args.output_dir, "instagram_leads.json")
    
    try:
        # Search for businesses
        if query.startswith("@"):
            # Search by username
            username = query[1:]  # Remove @ prefix
            profile = instagram_client.get_profile(username)
            posts = instagram_client.get_profile_posts(username, limit=limit)
            
            if not profile and not posts:
                logger.warning(f"No data found for Instagram profile: {username}")
                return 0
            
            # Combine profile and posts
            results = {"profile": profile, "posts": posts}
            
        elif query.startswith("#"):
            # Search by hashtag
            hashtag = query[1:]  # Remove # prefix
            results = instagram_client.search_hashtag(hashtag, limit=limit)
            
            if not results:
                logger.warning(f"No data found for Instagram hashtag: {hashtag}")
                return 0
        else:
            # General business search
            results = instagram_client.search_business(query, limit=limit)
            
            if not results:
                logger.warning(f"No data found for Instagram business search: {query}")
                return 0
        
        logger.info(f"Found Instagram data for query: {query}")
        
        # Standardize the data
        standardized_leads = []
        
        # Handle different result types
        if isinstance(results, dict) and "profile" in results:
            # Profile with posts
            lead = standardize_lead(results["profile"], "instagram")
            standardized_leads.append(lead)
            
            # Add leads from posts if they have contact info
            for post in results.get("posts", []):
                if any(contact_field in str(post) for contact_field in ["email", "phone", "contact", "@"]):
                    lead = standardize_lead(post, "instagram")
                    standardized_leads.append(lead)
        elif isinstance(results, list):
            # List of results
            for result in results:
                lead = standardize_lead(result, "instagram")
                standardized_leads.append(lead)
        else:
            # Single result
            lead = standardize_lead(results, "instagram")
            standardized_leads.append(lead)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_leads, f, indent=2)
        
        logger.info(f"Saved {len(standardized_leads)} standardized leads to {output_file}")
        
        # Save to CSV for backward compatibility
        csv_output_file = os.path.join(args.output_dir, "instagram_leads.csv")
        _convert_leads_to_csv(standardized_leads, csv_output_file)
        logger.info(f"Saved leads to CSV for compatibility: {csv_output_file}")
        
        return len(standardized_leads)
        
    except Exception as e:
        logger.error(f"Error in Instagram client: {str(e)}")
        return 0

def run_web_browser_client(args, logger):
    """Run the Web Browser client to collect business data."""
    logger.info("Starting Web Browser data collection")
    
    # Get the Web Browser client
    try:
        web_client = get_client('web_browser')
        if not web_client:
            logger.error("Failed to initialize Web Browser client. Check your API configuration.")
            return 0
    except Exception as e:
        logger.error(f"Error initializing Web Browser client: {str(e)}")
        return 0
    
    # Determine the search parameters
    if args.search:
        query = args.search
        logger.info(f"Searching with Web Browser using query: {query}")
    elif args.url:
        # Direct URL extraction
        query = args.url
        logger.info(f"Extracting content from URL: {query}")
    else:
        # Default to predefined queries
        queries = args.queries.split(",") if args.queries else WEB_SEARCH_QUERIES
        if args.limit_sources and len(queries) > args.limit_sources:
            queries = queries[:args.limit_sources]
        
        query = queries[0]
        logger.info(f"Searching with Web Browser using default query: {query}")
    
    # Determine result limit
    limit = args.limit if args.limit else 3  # Web browser typically needs fewer results
    logger.info(f"Limiting results to: {limit}")
    
    # Set up output file
    output_file = os.path.join(args.output_dir, "web_browser_leads.json")
    
    try:
        # Process based on input type
        if query.startswith(("http://", "https://")):
            # Direct URL extraction
            content = web_client.extract_from_url(url=query)
            
            if not content:
                logger.warning(f"No content extracted from URL: {query}")
                return 0
            
            results = [{"url": query, "content": content}]
        else:
            # Search query
            results = web_client.search_and_extract(
                query=query,
                max_results=limit
            )
            
            if not results:
                logger.warning(f"No results found for Web Browser search: {query}")
                return 0
        
        logger.info(f"Found {len(results)} web pages with Web Browser")
        
        # Standardize the data
        standardized_leads = []
        for result in results:
            try:
                lead = standardize_lead(result, "web_browser")
                standardized_leads.append(lead)
            except Exception as e:
                logger.error(f"Error standardizing lead data: {str(e)}")
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_leads, f, indent=2)
        
        logger.info(f"Saved {len(standardized_leads)} standardized leads to {output_file}")
        
        # Save to CSV for backward compatibility
        csv_output_file = os.path.join(args.output_dir, "web_browser_leads.csv")
        _convert_leads_to_csv(standardized_leads, csv_output_file)
        logger.info(f"Saved leads to CSV for compatibility: {csv_output_file}")
        
        return len(standardized_leads)
        
    except Exception as e:
        logger.error(f"Error in Web Browser client: {str(e)}")
        return 0

def _convert_leads_to_csv(leads, csv_file):
    """Convert standardized leads to CSV format for compatibility."""
    if not leads:
        return
        
    # Define the CSV fields
    fields = [
        "organization", "person_name", "role", "email", "phone", 
        "address", "city", "state", "postal_code", "website", 
        "industry", "source", "timestamp"
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for lead in leads:
            # Extract flat fields for CSV
            row = {field: lead.get(field, "") for field in fields}
            writer.writerow(row)

def enrich_and_deduplicate_leads(args, logger):
    """Load leads from all sources, enrich, and deduplicate them."""
    logger.info("Starting lead enrichment and deduplication process")
    
    all_leads = []
    
    # Load leads from all source files
    sources = [
        ("google_maps_leads.json", "google_maps"),
        ("instagram_leads.json", "instagram"),
        ("web_browser_leads.json", "web_browser"),
        ("yellow_pages_leads.csv", "yellow_pages"),
        ("gov_ministry_leads.csv", "government"),
        ("university_leads.csv", "university")
    ]
    
    for filename, source_type in sources:
        filepath = os.path.join(args.output_dir, filename)
        if not os.path.exists(filepath):
            continue
            
        logger.info(f"Loading leads from {filepath}")
        
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    source_leads = json.load(f)
            else:  # CSV file
                source_leads = []
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        source_leads.append(row)
            
            # Add source type if not present
            for lead in source_leads:
                if "source" not in lead or not lead["source"]:
                    lead["source"] = source_type
            
            all_leads.extend(source_leads)
            logger.info(f"Added {len(source_leads)} leads from {source_type}")
        except Exception as e:
            logger.error(f"Error loading leads from {filepath}: {str(e)}")
    
    if not all_leads:
        logger.warning("No leads found to process")
        return 0
    
    logger.info(f"Total leads loaded: {len(all_leads)}")
    
    # Enrich and deduplicate
    try:
        # Filter by completeness if requested
        if args.min_score:
            min_score = float(args.min_score)
            filtered_leads = filter_leads_by_completeness(all_leads, min_score)
            logger.info(f"Filtered leads by completeness score >= {min_score}: {len(filtered_leads)} of {len(all_leads)} remaining")
            all_leads = filtered_leads
        
        # Deduplicate leads
        unique_leads = deduplicate_leads(all_leads)
        logger.info(f"After deduplication: {len(unique_leads)} unique leads")
        
        # Save the enriched and deduplicated leads
        output_file = os.path.join(args.output_dir, args.output_file)
        
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_leads, f, indent=2)
        else:  # CSV
            _convert_leads_to_csv(unique_leads, output_file)
        
        logger.info(f"Saved {len(unique_leads)} enriched and deduplicated leads to {output_file}")
        
        return len(unique_leads)
        
    except Exception as e:
        logger.error(f"Error during lead enrichment and deduplication: {str(e)}")
        return 0

def main():
    """Main entry point of the lead generator."""
    parser = argparse.ArgumentParser(description="Malaysian Lead Generator CLI")
    
    # Create argument groups for better organization
    api_group = parser.add_argument_group("MCP-Powered API Options (Recommended)")
    legacy_scraping_group = parser.add_argument_group("Legacy Scraping Options (Deprecated)")
    email_gen_group = parser.add_argument_group("Email Generation Options")
    email_send_group = parser.add_argument_group("Email Sending Options")
    general_group = parser.add_argument_group("General Options")
    
    # MCP-Powered API options (Recommended)
    api_group.add_argument("--use-google-maps", action="store_true", help="Use Google Maps API for business data")
    api_group.add_argument("--use-instagram", action="store_true", help="Use Instagram API for social media data")
    api_group.add_argument("--use-web-browser", action="store_true", help="Use Web Browser API for website content")
    api_group.add_argument("--search", type=str, help="Search query for data sources")
    api_group.add_argument("--location", type=str, help="Location for Google Maps search (e.g., 'Kuala Lumpur')")
    api_group.add_argument("--categories", type=str, help="Comma-separated business categories (for Google Maps)")
    api_group.add_argument("--hashtags", type=str, help="Comma-separated hashtags (for Instagram)")
    api_group.add_argument("--queries", type=str, help="Comma-separated search queries (for Web Browser)")
    api_group.add_argument("--url", type=str, help="Specific URL to extract data from (for Web Browser)")
    api_group.add_argument("--multi-source", action="store_true", help="Use multiple data sources and enrich leads")
    api_group.add_argument("--min-score", type=float, default=0.3, help="Minimum completeness score for leads (0.0-1.0)")
    
    # Legacy scraping options (Deprecated)
    legacy_scraping_group.add_argument("--use-yellowpages", action="store_true", help="Scrape from Yellow Pages Malaysia (DEPRECATED)")
    legacy_scraping_group.add_argument("--use-businesslist", action="store_true", help="Scrape from BusinessList.my (DEPRECATED)")
    legacy_scraping_group.add_argument("--use-gov-ministry", action="store_true", help="Scrape from government ministry websites (DEPRECATED)")
    legacy_scraping_group.add_argument("--use-university", action="store_true", help="Scrape from university websites (DEPRECATED)")
    legacy_scraping_group.add_argument("--yp-categories", type=str, help="Categories to scrape from Yellow Pages/BusinessList")
    legacy_scraping_group.add_argument("--gov-websites", type=str, help="Government websites to scrape")
    legacy_scraping_group.add_argument("--uni-websites", type=str, help="University websites to scrape")
    legacy_scraping_group.add_argument("--max-pages-per-source", type=int, default=5, help="Maximum pages to scrape per source")
    legacy_scraping_group.add_argument("--min-delay", type=float, default=2.0, help="Minimum delay between requests")
    legacy_scraping_group.add_argument("--max-delay", type=float, default=5.0, help="Maximum delay between requests")
    
    # Common options
    general_group.add_argument("--limit", type=int, help="Limit the number of results to collect")
    general_group.add_argument("--limit-sources", type=int, help="Limit the number of sources to collect from")
    general_group.add_argument("--output-dir", type=str, default="output", help="Directory to save output files")
    general_group.add_argument("--output-file", type=str, default="all_leads.json", help="Name of combined output file")
    general_group.add_argument("--import-to-db", action="store_true", help="Import leads to database")
    general_group.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    
    # Email generation options
    email_gen_group.add_argument("--generate-emails", action="store_true", help="Generate emails for leads")
    email_gen_group.add_argument("--email-template", type=str, choices=["default", "government", "university", "retreat", "cost", "exec_tone"], help="Email template to use")
    email_gen_group.add_argument("--lead-status", type=str, default="NEW", choices=["NEW", "CONTACTED", "RESPONDED", "QUALIFIED", "DISQUALIFIED"], help="Generate emails for leads with this status")
    email_gen_group.add_argument("--force-generation", action="store_true", help="Force email generation even if recently generated")
    email_gen_group.add_argument("--update-status", action="store_true", help="Update lead status after email generation")
    email_gen_group.add_argument("--email-output-dir", type=str, help="Directory to save generated email files")
    
    # Email sending options
    email_send_group.add_argument("--send-emails", action="store_true", help="Send generated emails")
    email_send_group.add_argument("--dry-run", action="store_true", help="Validate but don't actually send emails")
    email_send_group.add_argument("--smtp-server", type=str, help="SMTP server address")
    email_send_group.add_argument("--smtp-port", type=int, default=587, help="SMTP server port")
    email_send_group.add_argument("--smtp-username", type=str, help="SMTP username")
    email_send_group.add_argument("--smtp-password", type=str, help="SMTP password")
    email_send_group.add_argument("--from-email", type=str, help="Sender email address")
    email_send_group.add_argument("--from-name", type=str, help="Sender name")
    email_send_group.add_argument("--email-rate-limit", type=int, default=100, help="Maximum emails per hour")
    email_send_group.add_argument("--email-batch-size", type=int, default=10, help="Number of emails to send per batch")
    email_send_group.add_argument("--attach-proposal", type=str, help="Path to PDF proposal to attach to emails")
    email_send_group.add_argument("--proposal-dir", type=str, help="Directory containing PDF proposals to select from")
    email_send_group.add_argument("--use-package-selection", action="store_true", 
                                 help="Use intelligent package-based proposal selection")
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize API clients
    try:
        activate_clients()
        logger.info("MCP-powered API clients activated")
    except Exception as e:
        logger.error(f"Error activating API clients: {str(e)}")
        logger.error("Some data collection functions may not be available")
    
    # Variable to track if we need to import leads
    leads_collected = False
    combined_file = os.path.join(args.output_dir, args.output_file)
    
    # Check if any data source is specified
    mcp_sources_selected = args.use_google_maps or args.use_instagram or args.use_web_browser
    legacy_sources_selected = args.use_yellowpages or args.use_gov_ministry or args.use_university or args.use_businesslist
    
    # If no specific source is selected, use Google Maps by default
    if not mcp_sources_selected and not legacy_sources_selected:
        logger.info("No specific data source selected, using Google Maps by default")
        args.use_google_maps = True
    
    # Prioritize MCP-powered data sources
    total_leads = 0
    
    if mcp_sources_selected:
        logger.info("Starting data collection with MCP-powered data sources")
        
        # If multi-source is specified, try to get data from all available sources
        if args.multi_source:
            logger.info("Running multi-source data collection")
            
            if not args.use_google_maps and not args.use_instagram and not args.use_web_browser:
                # Enable all sources for multi-source collection
                args.use_google_maps = args.use_instagram = args.use_web_browser = True
            
            if args.use_google_maps:
                total_leads += run_google_maps_client(args, logger)
            
            if args.use_instagram:
                total_leads += run_instagram_client(args, logger)
            
            if args.use_web_browser:
                total_leads += run_web_browser_client(args, logger)
            
            # Enrich and deduplicate leads from all sources
            total_leads = enrich_and_deduplicate_leads(args, logger)
            
        else:
            # Run individual data sources
            if args.use_google_maps:
                total_leads += run_google_maps_client(args, logger)
            
            if args.use_instagram:
                total_leads += run_instagram_client(args, logger)
            
            if args.use_web_browser:
                total_leads += run_web_browser_client(args, logger)
            
            # If multiple sources were used, combine them
            if sum([args.use_google_maps, args.use_instagram, args.use_web_browser]) > 1:
                total_leads = enrich_and_deduplicate_leads(args, logger)
        
        logger.info(f"MCP-powered data collection completed. Total leads: {total_leads}")
        leads_collected = True
    
    # Fallback to legacy scrapers if specifically requested
    if legacy_sources_selected:
        logger.warning("Using deprecated scraping methods. Consider migrating to MCP-powered data sources.")
        logger.info("Starting legacy scraper data collection")
        
        if args.use_yellowpages or args.use_businesslist:
            total_leads += run_yellow_pages_scraper(args, logger)
        
        if args.use_gov_ministry:
            total_leads += run_gov_ministry_scraper(args, logger)
        
        if args.use_university:
            total_leads += run_university_scraper(args, logger)
        
        # Combine results from legacy scrapers
        if leads_collected:
            # We already have MCP data, so merge with legacy data
            total_leads = enrich_and_deduplicate_leads(args, logger)
        else:
            # Only legacy data, use old combination method
            combine_csv_files(args.output_dir, combined_file, logger)
        
        logger.info(f"Legacy data collection completed. Total leads: {total_leads}")
        leads_collected = True
    
    # Import leads to database if needed
    if leads_collected and args.import_to_db:
        logger.info("Importing leads to database")
        import_leads_to_database(combined_file, logger)
    elif args.import_to_db and args.output_file:
        # Try to import from the specified output file
        file_path = os.path.join(args.output_dir, args.output_file)
        if os.path.exists(file_path):
            logger.info(f"Importing leads from existing file: {file_path}")
            import_leads_to_database(file_path, logger)
        else:
            logger.error(f"Cannot import leads: file not found: {file_path}")
    
    # Email generation phase
    emails_to_send = []
    if args.generate_emails:
        logger.info("Starting email generation phase")
        emails_to_send = generate_emails(args, logger)
    
    # Email sending phase
    if args.send_emails and emails_to_send:
        logger.info("Starting email sending phase")
        
        # Check for required parameters
        if not args.smtp_server or not args.smtp_username or not args.smtp_password or not args.from_email:
            logger.error("Missing required SMTP parameters for sending emails")
            logger.error("Required: --smtp-server, --smtp-username, --smtp-password, --from-email")
            return
        
        send_emails(emails_to_send, args, logger)

if __name__ == "__main__":
    main() 