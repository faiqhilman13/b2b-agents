from lead_generator.agents.scraper import fetch_page, parse_contacts, save_to_csv, get_all_links
import logging
import time
import random
from bs4 import BeautifulSoup
import re

logger = logging.getLogger('lead_generator.yellowpages')

class YellowPagesScraper:
    """Specialized scraper for Yellow Pages Malaysia or BusinessList.my"""
    
    def __init__(self, base_url="https://www.yellowpages.my", output_file="leads_yellowpages.csv"):
        self.base_url = base_url
        self.output_file = output_file
        
    def scrape_category(self, category, max_pages=5, delay_range=(3, 7)):
        """
        Scrape a specific category on Yellow Pages or BusinessList.my
        
        Args:
            category (str): Category slug to scrape 
            max_pages (int): Maximum number of pagination pages to scrape
            delay_range (tuple): Range for random delay between requests
            
        Returns:
            int: Total number of leads collected
        """
        total_leads = 0
        
        # Adapt URL format based on the site we're using
        if self.base_url == "https://www.businesslist.my":
            # BusinessList.my uses a simple category structure
            category_url = f"{self.base_url}/category/{category}"
            logger.info(f"Using BusinessList.my URL: {category_url}")
        elif self.base_url == "https://www.yellowpages.my":
            # Yellow Pages Malaysia uses a different URL structure
            category_url = f"{self.base_url}/services/l/{category}"
            logger.info(f"Using YellowPages.my URL: {category_url}")
        else:
            # Fallback for any other site
            category_url = f"{self.base_url}/category/{category}"
            logger.info(f"Using fallback URL structure: {category_url}")
        
        logger.info(f"Starting to scrape category: {category} from {self.base_url}")
        
        for page_num in range(1, max_pages + 1):
            # Construct pagination URL - BusinessList.my uses a different parameter
            if self.base_url == "https://www.businesslist.my":
                page_url = f"{category_url}/page-{page_num}" if page_num > 1 else category_url
            else:
                page_url = f"{category_url}?page={page_num}" if page_num > 1 else category_url
            
            logger.info(f"Fetching page {page_num}: {page_url}")
            
            # Fetch the category page
            html = fetch_page(page_url)
            if not html:
                logger.warning(f"Failed to fetch page {page_num} for category {category}")
                continue
                
            # Parse the listing page to get links to business profiles
            business_links = self._extract_business_links(html)
            logger.info(f"Found {len(business_links)} business links on page {page_num}")
            
            # Process each business profile
            for business_url in business_links:
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(*delay_range))
                
                # Fetch and parse the business profile
                business_html = fetch_page(business_url)
                if not business_html:
                    continue
                    
                # Parse contacts using specialized parser for Yellow Pages
                contacts = self._parse_yellowpages_contacts(business_html, business_url)
                
                # Save the leads
                if contacts:
                    num_saved = save_to_csv(contacts, self.output_file)
                    total_leads += num_saved
                    
            logger.info(f"Completed page {page_num}/{max_pages} for category {category}")
            
            # Check if there are more pages
            if not self._has_next_page(html, page_num):
                logger.info(f"No more pages available for category {category}")
                break
                
            # Add delay between pagination pages
            time.sleep(random.uniform(*delay_range))
            
        logger.info(f"Completed scraping category {category}. Total leads: {total_leads}")
        return total_leads
        
    def _extract_business_links(self, html):
        """Extract links to business profiles from a category page"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        if self.base_url == "https://www.businesslist.my":
            # BusinessList.my structure
            listings = soup.find_all('div', class_='company')
            logger.info(f"Found {len(listings)} company listings on page")
            
            for listing in listings:
                # Find the link to the business profile
                link_element = listing.find('a', class_='link_search', href=True)
                if link_element:
                    # BusinessList.my typically uses relative URLs
                    href = link_element['href']
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    links.append(full_url)
                    logger.debug(f"Added business link: {full_url}")
                else:
                    # Try finding any link with company information
                    link_element = listing.find('a', href=True)
                    if link_element and '/company/' in link_element['href']:
                        href = link_element['href']
                        full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                        links.append(full_url)
                        logger.debug(f"Added business link via alternate method: {full_url}")
                    
        elif self.base_url == "https://www.yellowpages.my":
            # Yellow Pages Malaysia structure
            listings = soup.find_all('div', class_=lambda c: c and ('listing-item' in c or 'business-card' in c or 'business-listing' in c))
            logger.info(f"Found {len(listings)} business listings on page")
            
            for listing in listings:
                # Find the link to the business profile
                link_element = listing.find('a', href=True)
                if link_element and ('/business/' in link_element['href'] or '/profile/' in link_element['href']):
                    href = link_element['href']
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    links.append(full_url)
                    logger.debug(f"Added business link: {full_url}")
        else:
            # Generic fallback structure
            listings = soup.find_all('div', class_=lambda c: c and ('listing' in c or 'business-card' in c))
            logger.info(f"Found {len(listings)} listings on page (generic structure)")
            
            for listing in listings:
                # Find the link to the business profile
                link_element = listing.find('a', href=True)
                if link_element:
                    href = link_element['href']
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    links.append(full_url)
                    logger.debug(f"Added business link: {full_url}")
                
        return links
        
    def _parse_yellowpages_contacts(self, html, source_url):
        """Parse contacts from a Yellow Pages business profile"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        contacts = []
        
        # Extract organization name
        organization = self._extract_yellowpages_organization(soup)
        
        # Extract person names and roles
        people = self._extract_yellowpages_people(soup)
        
        # If no specific people found, create a generic entry for the organization
        if not people:
            # Extract contact details
            email = self._extract_yellowpages_email(soup)
            phone = self._extract_yellowpages_phone(soup)
            
            if organization or email or phone:
                contacts.append({
                    'organization': organization,
                    'person_name': '',  # No specific person
                    'role': '',
                    'email': email,
                    'phone': phone,
                    'source_url': source_url
                })
        else:
            # For each person found, create a separate entry
            for person in people:
                contacts.append({
                    'organization': organization,
                    'person_name': person.get('name', ''),
                    'role': person.get('role', ''),
                    'email': person.get('email', self._extract_yellowpages_email(soup)),
                    'phone': person.get('phone', self._extract_yellowpages_phone(soup)),
                    'source_url': source_url
                })
                
        return contacts
        
    def _extract_yellowpages_organization(self, soup):
        """Extract organization name from Yellow Pages business profile"""
        # Try to find the business name in the header
        org_element = soup.find(['h1', 'h2'], class_=lambda c: c and ('business-name' in c or 'title' in c))
        if org_element:
            return org_element.get_text(strip=True)
            
        # Alternative: look for structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'name' in data:
                    return data['name']
            except:
                pass
                
        # Fallback to title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            return title.split('|')[0].strip()
            
        return ''
        
    def _extract_yellowpages_people(self, soup):
        """Extract people information from Yellow Pages business profile"""
        people = []
        
        # Look for sections that might contain people info
        people_sections = soup.find_all(['div', 'section'], class_=lambda c: c and ('people' in str(c).lower() or 'team' in str(c).lower() or 'staff' in str(c).lower() or 'management' in str(c).lower()))
        
        for section in people_sections:
            person_elements = section.find_all(['div', 'li'], class_=lambda c: c and ('person' in str(c).lower() or 'member' in str(c).lower()))
            
            for element in person_elements:
                name = ''
                role = ''
                
                # Extract name
                name_element = element.find(['h3', 'h4', 'strong', 'b'])
                if name_element:
                    name = name_element.get_text(strip=True)
                
                # Extract role
                role_element = element.find(['p', 'span', 'div'], class_=lambda c: c and ('role' in str(c).lower() or 'title' in str(c).lower() or 'position' in str(c).lower()))
                if role_element:
                    role = role_element.get_text(strip=True)
                
                if name:
                    people.append({
                        'name': name,
                        'role': role,
                        'email': '',  # Individual emails often not available, will use generic
                        'phone': ''   # Individual phones often not available, will use generic
                    })
        
        return people
        
    def _extract_yellowpages_email(self, soup):
        """Extract email from Yellow Pages business profile"""
        # Look for elements containing email
        email_elements = soup.find_all(['a', 'span', 'div'], string=lambda s: s and '@' in s)
        
        for element in email_elements:
            text = element.get_text()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                return emails[0]
                
        # Look for mailto links
        mailto_links = soup.find_all('a', href=lambda h: h and h.startswith('mailto:'))
        for link in mailto_links:
            email = link['href'].replace('mailto:', '').split('?')[0]
            if '@' in email:
                return email
                
        return ''
        
    def _extract_yellowpages_phone(self, soup):
        """Extract phone number from Yellow Pages business profile"""
        # Look for elements containing phone numbers
        phone_elements = soup.find_all(['span', 'div', 'a'], string=lambda s: s and re.search(r'\d{3}[-\s]?\d{3,4}[-\s]?\d{3,4}', str(s)))
        
        for element in phone_elements:
            text = element.get_text()
            # Malaysian phone patterns
            phone_patterns = [
                r'\+?6?01\d[ -]?\d{3}[ -]?\d{4}',  # Mobile
                r'\+?6?0\d[ -]?\d{7,8}',           # Landline
                r'\+?6?0\d{1,2}[ -]?\d{3}[ -]?\d{4}'  # Various formats
            ]
            
            for pattern in phone_patterns:
                phones = re.findall(pattern, text)
                if phones:
                    return phones[0]
                    
        # Look for tel links
        tel_links = soup.find_all('a', href=lambda h: h and h.startswith('tel:'))
        for link in tel_links:
            phone = link['href'].replace('tel:', '')
            return phone
            
        return ''
        
    def _has_next_page(self, html, current_page):
        """Check if there is a next page in pagination"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find pagination elements
        pagination = soup.find(['div', 'ul', 'nav'], class_=lambda c: c and ('pagination' in c or 'pager' in c))
        if not pagination:
            return False
            
        # Check if there's a next button or a page number higher than the current page
        next_button = pagination.find('a', string=lambda s: s and ('next' in s.lower() or '›' in s or '»' in s))
        if next_button:
            return True
            
        # Check for page numbers
        page_links = pagination.find_all('a')
        for link in page_links:
            try:
                page_num = int(link.get_text(strip=True))
                if page_num > current_page:
                    return True
            except ValueError:
                continue
                
        return False
        
    def scrape_multiple_categories(self, categories, max_pages_per_category=3, delay_between_categories=(5, 10)):
        """
        Scrape multiple categories
        
        Args:
            categories (list): List of category slugs to scrape
            max_pages_per_category (int): Maximum pages to scrape per category
            delay_between_categories (tuple): Range for random delay between categories
            
        Returns:
            int: Total number of leads collected
        """
        total_leads = 0
        
        for category in categories:
            leads = self.scrape_category(category, max_pages=max_pages_per_category)
            total_leads += leads
            
            # Add delay between categories
            if category != categories[-1]:  # Skip delay after the last category
                delay = random.uniform(*delay_between_categories)
                logger.info(f"Waiting {delay:.1f} seconds before next category...")
                time.sleep(delay)
                
        return total_leads 