#!/usr/bin/env python3
"""
Test script for the lead generation scrapers.

This script performs basic tests to ensure that the scrapers
are working correctly by running them on a small number of pages.
"""

import os
import sys
import logging
import time
from datetime import datetime

# Make sure we can import from the current directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our scrapers
from lead_generator.yellow_pages_scraper import YellowPagesScraper
from lead_generator.gov_ministry_scraper import GovMinistryScraper
from lead_generator.university_scraper import UniversityScraper
from lead_generator.scraper import fetch_page

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("lead_generator_test")

def test_fetch_page():
    """Test basic page fetching functionality."""
    logger.info("Testing page fetch functionality...")
    
    # Test with a reliable website
    url = "https://www.google.com"
    html = fetch_page(url)
    
    if html:
        logger.info("[PASS] Page fetch successful")
        return True
    else:
        logger.error("[FAIL] Page fetch failed")
        return False

def test_yellow_pages_scraper():
    """Test the Yellow Pages scraper with a single category and limited pages."""
    logger.info("Testing Yellow Pages scraper...")
    
    # Create output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Initialize scraper with test output file
    output_file = "test_output/yellow_pages_test.csv"
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Test with Yellow Pages Malaysia
    try:
        logger.info("Attempting to scrape a single Yellow Pages category page...")
        scraper = YellowPagesScraper(base_url="https://www.yellowpages.my", output_file=output_file)
        leads = scraper.scrape_category("education", max_pages=1)
        
        if os.path.exists(output_file):
            logger.info(f"[PASS] Yellow Pages scraper test successful - found {leads} leads")
            return True
        else:
            logger.warning("[WARN] Yellow Pages scraper did not create output file, but did not error")
            
            # Try with BusinessList.my as a fallback
            logger.info("Trying with BusinessList.my as a fallback...")
            if os.path.exists(output_file):
                os.remove(output_file)
                
            scraper = YellowPagesScraper(base_url="https://www.businesslist.my", output_file=output_file)
            leads = scraper.scrape_category("education", max_pages=1)
            
            if os.path.exists(output_file):
                logger.info(f"[PASS] BusinessList.my scraper test successful - found {leads} leads")
                return True
            else:
                logger.warning("[WARN] BusinessList.my scraper did not create output file either")
                return False
    except Exception as e:
        logger.error(f"[FAIL] Directory scraper test failed: {e}")
        return False

def test_gov_ministry_scraper():
    """Test the Government Ministry scraper with a single website and limited pages."""
    logger.info("Testing Government Ministry scraper...")
    
    # Create output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Initialize scraper with test output file
    output_file = "test_output/gov_ministry_test.csv"
    if os.path.exists(output_file):
        os.remove(output_file)
        
    scraper = GovMinistryScraper(output_file=output_file)
    
    # Test with a single ministry website and only a few pages
    try:
        logger.info("Attempting to scrape a single government ministry page...")
        # Use a more stable government site for testing
        leads = scraper.scrape_ministry("https://www.malaysia.gov.my", max_pages=2, max_depth=1)
        
        if os.path.exists(output_file):
            logger.info(f"[PASS] Government Ministry scraper test successful - found {leads} leads")
            return True
        else:
            logger.warning("[WARN] Government Ministry scraper did not create output file, but did not error")
            return False
    except Exception as e:
        logger.error(f"[FAIL] Government Ministry scraper test failed: {e}")
        return False

def test_university_scraper():
    """Test the University scraper with a single website and limited pages."""
    logger.info("Testing University scraper...")
    
    # Create output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Initialize scraper with test output file
    output_file = "test_output/university_test.csv"
    if os.path.exists(output_file):
        os.remove(output_file)
        
    scraper = UniversityScraper(output_file=output_file)
    
    # Test with a single university website and only a few pages
    try:
        logger.info("Attempting to scrape a single university page...")
        leads = scraper.scrape_university("https://www.um.edu.my", max_pages=2, max_depth=1)
        
        if os.path.exists(output_file):
            logger.info(f"[PASS] University scraper test successful - found {leads} leads")
            return True
        else:
            logger.warning("[WARN] University scraper did not create output file, but did not error")
            return False
    except Exception as e:
        logger.error(f"[FAIL] University scraper test failed: {e}")
        return False

def run_all_tests():
    """Run all test functions and report results."""
    logger.info("Starting lead generator tests...")
    
    # Create output directories
    os.makedirs("test_output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    test_results = {
        "fetch_page": test_fetch_page(),
        "yellow_pages": test_yellow_pages_scraper(),
        "gov_ministry": test_gov_ministry_scraper(),
        "university": test_university_scraper()
    }
    
    # Print summary
    logger.info("\n--- Test Results Summary ---")
    for test_name, result in test_results.items():
        status = "[PASS]" if result else "[FAIL]"
        logger.info(f"{test_name}: {status}")
    
    # Calculate overall result
    all_passed = all(test_results.values())
    logger.info(f"\nOverall Result: {'[PASS] All tests passed!' if all_passed else '[FAIL] Some tests failed.'}")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests() 