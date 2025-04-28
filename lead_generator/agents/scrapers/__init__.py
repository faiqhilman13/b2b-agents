"""
Legacy web scraper modules for targeted data acquisition.

Note: These scrapers are considered deprecated in favor of MCP-powered
Apify Actor integrations. They are maintained for reference and
may be used for targeted enrichment in limited cases.
"""

# Import legacy scrapers
# These are deprecated but maintained for reference
from ..scraper import fetch_page, parse_contacts, save_to_csv, get_all_links
from ..yellow_pages_scraper import YellowPagesScraper
from ..gov_ministry_scraper import GovMinistryScraper
from ..university_scraper import UniversityScraper

__all__ = [
    'fetch_page', 'parse_contacts', 'save_to_csv', 'get_all_links',
    'YellowPagesScraper', 'GovMinistryScraper', 'UniversityScraper'
] 