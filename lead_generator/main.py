#!/usr/bin/env python3
"""
Lead Generator - Malaysian Business Contact Collection Tool

This tool helps collect business leads from various Malaysian sources including:
- Yellow Pages Malaysia
- Government ministry websites
- University staff directories
- Chambers of commerce

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
from lead_generator.database.models import init_db, Lead, LeadStatus
from lead_generator.database.queries import LeadQueries
from sqlalchemy.orm import sessionmaker
from lead_generator.config.email_config import EMAIL_VALIDATION
from lead_generator.config.proposal_config import get_package_pdf, list_available_packages

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

def import_leads_to_database(csv_file, logger):
    """Import leads from CSV file to database."""
    logger.info(f"Importing leads from {csv_file} to database")
    
    # Initialize database
    db_path = "leads.db"
    engine = init_db(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    queries = LeadQueries(session)
    
    # Import leads
    total_imported = 0
    total_skipped = 0
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if email is valid
            if not row.get('email') or not EmailValidator.validate_email(row.get('email'))[0]:
                logger.debug(f"Skipping lead with invalid email: {row.get('email')}")
                total_skipped += 1
                continue
                
            # Check if lead already exists
            existing_lead = queries.get_lead(row.get('email'))
            if existing_lead:
                logger.debug(f"Lead already exists: {row.get('email')}")
                total_skipped += 1
                continue
                
            # Save lead to database
            lead_data = {
                'organization': row.get('organization', ''),
                'person_name': row.get('person_name', ''),
                'role': row.get('role', ''),
                'email': row.get('email', ''),
                'phone': row.get('phone', ''),
                'source_url': row.get('source_url', '')
            }
            
            queries.save_lead(lead_data)
            total_imported += 1
    
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

def main():
    """Main entry point of the lead generator."""
    parser = argparse.ArgumentParser(description="Malaysian Lead Generator CLI")
    
    # Create argument groups for better organization
    scraping_group = parser.add_argument_group("Scraping Options")
    email_gen_group = parser.add_argument_group("Email Generation Options")
    email_send_group = parser.add_argument_group("Email Sending Options")
    general_group = parser.add_argument_group("General Options")
    
    # Scraping options
    scraping_group.add_argument("--use-yellowpages", action="store_true", help="Scrape from Yellow Pages Malaysia")
    scraping_group.add_argument("--use-businesslist", action="store_true", help="Scrape from BusinessList.my")
    scraping_group.add_argument("--use-gov-ministry", action="store_true", help="Scrape from government ministry websites")
    scraping_group.add_argument("--use-university", action="store_true", help="Scrape from university websites")
    scraping_group.add_argument("--limit", type=int, help="Limit the number of results to scrape")
    scraping_group.add_argument("--category", type=str, help="Category to scrape from (for Yellow Pages/BusinessList)")
    scraping_group.add_argument("--categories-file", type=str, help="File containing categories to scrape")
    scraping_group.add_argument("--ministries-file", type=str, help="File containing ministry URLs to scrape")
    scraping_group.add_argument("--universities-file", type=str, help="File containing university URLs to scrape")
    scraping_group.add_argument("--delay", type=float, help="Delay between requests in seconds")
    scraping_group.add_argument("--limit-sources", type=int, help="Limit the number of sources to scrape from each category")
    
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
    
    # General options
    general_group.add_argument("--output-dir", type=str, default="output", help="Directory to save output files")
    general_group.add_argument("--output-file", type=str, default="all_leads.csv", help="Name of combined output file")
    general_group.add_argument("--import-to-db", action="store_true", help="Import leads to database")
    general_group.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Variable to track if we need to import leads
    leads_collected = False
    combined_file = None
    
    # Scraping phase
    if args.use_yellowpages or args.use_gov_ministry or args.use_university:
        logger.info("Starting lead collection phase")
        
        # Select sources to scrape if not specified
        if not (args.use_yellowpages or args.use_gov_ministry or args.use_university):
            logger.info("No specific source specified, defaulting to all sources")
            args.use_yellowpages = args.use_gov_ministry = args.use_university = True
        
        # Scrape selected sources
        total_leads = 0
        
        if args.use_yellowpages:
            total_leads += run_yellow_pages_scraper(args, logger)
        
        if args.use_gov_ministry:
            total_leads += run_gov_ministry_scraper(args, logger)
        
        if args.use_university:
            total_leads += run_university_scraper(args, logger)
        
        # Combine results into a single file
        combined_file = os.path.join(args.output_dir, args.output_file)
        combine_csv_files(args.output_dir, combined_file, logger)
        
        logger.info(f"Lead generation completed. Total leads collected: {total_leads}")
        logger.info(f"Combined leads saved to: {combined_file}")
        
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