import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import time
from urllib.parse import urljoin, urlparse
import logging
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lead_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('lead_generator')

def fetch_page(url, headers=None, timeout=30, retries=3):
    """
    Makes an HTTP request and returns the page content.
    
    Args:
        url (str): The URL to fetch
        headers (dict, optional): HTTP headers to use
        timeout (int, optional): Request timeout in seconds
        retries (int, optional): Number of retry attempts
        
    Returns:
        str: HTML content of the page or None if failed
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    # Use a session to maintain cookies
    session = requests.Session()
    
    # First make a request to the site's homepage to get cookies
    if 'businesslist.my' in url or 'yellowpages.my' in url:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        try:
            session.get(base_url, headers=headers, timeout=timeout)
            logger.info(f"Established session with {base_url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not establish session with {base_url}: {e}")
    
    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url}")
            # Add a small random delay before the request to seem more human-like
            time.sleep(random.uniform(0.5, 1.5))
            
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return None

def parse_contacts(html, source_url):
    """
    Parses HTML content to extract contact information.
    
    Args:
        html (str): HTML content of the page
        source_url (str): The URL where the HTML was fetched from
        
    Returns:
        list: List of dictionaries containing contact information
    """
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    contacts = []
    organization = extract_organization(soup, source_url)
    
    logger.info(f"Parsing contacts from {source_url}")
    
    # Strategy 1: Extract from tables (common in directories)
    table_contacts = _extract_contacts_from_tables(soup, organization, source_url)
    contacts.extend(table_contacts)
    logger.debug(f"Found {len(table_contacts)} contacts in tables")
    
    # Strategy 2: Extract from structured divs/sections
    section_contacts = _extract_contacts_from_sections(soup, organization, source_url)
    contacts.extend(section_contacts)
    logger.debug(f"Found {len(section_contacts)} contacts in structured sections")
    
    # Strategy 3: Extract from paragraphs with contact hints
    paragraph_contacts = _extract_contacts_from_paragraphs(soup, organization, source_url)
    contacts.extend(paragraph_contacts)
    logger.debug(f"Found {len(paragraph_contacts)} contacts in paragraphs")
    
    # Strategy 4: Extract from list items
    list_contacts = _extract_contacts_from_lists(soup, organization, source_url)
    contacts.extend(list_contacts)
    logger.debug(f"Found {len(list_contacts)} contacts in list items")
    
    # Final count
    logger.info(f"Total contacts extracted from {source_url}: {len(contacts)}")
    return contacts

def _extract_contacts_from_tables(soup, organization, source_url):
    """Extract contacts from HTML tables"""
    contacts = []
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:  # Assuming at least name and one contact method
                # Try to find email and phone in any cell
                email = ''
                phone = ''
                person_name = ''
                role = ''
                
                # First cell often contains person name
                if cells:
                    person_name = extract_text(cells[0])
                
                # Second cell often contains role/title
                if len(cells) > 1:
                    role = extract_text(cells[1])
                
                # Look for email and phone in all cells
                for cell in cells:
                    cell_text = cell.get_text()
                    if not email:
                        email = extract_email(cell_text)
                    if not phone:
                        phone = extract_phone(cell_text)
                
                # If we have at least some useful information, create a contact
                if person_name or email or phone:
                    contact = {
                        'organization': organization,
                        'person_name': person_name,
                        'role': role,
                        'email': email,
                        'phone': phone,
                        'source_url': source_url
                    }
                    contacts.append(contact)
    
    return contacts

def _extract_contacts_from_sections(soup, organization, source_url):
    """Extract contacts from structured divs/sections with contact information"""
    contacts = []
    
    # Find contact sections with various naming patterns
    contact_sections = soup.find_all(['div', 'section'], class_=lambda c: c and any(keyword in str(c).lower() 
                                                                          for keyword in ['contact', 'team', 'staff', 'directory', 'people']))
    
    for section in contact_sections:
        # Find potential contact info containers
        person_elements = section.find_all(['div', 'li', 'article'])
        for element in person_elements:
            name = extract_name(element)
            if name:
                contact = {
                    'organization': organization,
                    'person_name': name,
                    'role': extract_role(element),
                    'email': extract_email(element.get_text()),
                    'phone': extract_phone(element.get_text()),
                    'source_url': source_url
                }
                contacts.append(contact)
    
    return contacts

def _extract_contacts_from_paragraphs(soup, organization, source_url):
    """Extract contacts from paragraphs with contact information"""
    contacts = []
    
    # Look for paragraphs that might contain contact information
    for p in soup.find_all("p"):
        p_text = p.get_text()
        
        # Skip very short paragraphs that are unlikely to contain contact info
        if len(p_text) < 10:
            continue
            
        # Check if paragraph contains contact indicators
        contact_indicators = ["@", "email", "phone", "tel", "contact", "officer", "manager", "director", 
                             "pengarah", "pegawai", "telefon", "emel", "hubungi"]
        
        if any(indicator in p_text.lower() for indicator in contact_indicators):
            name = extract_name(p)
            email = extract_email(p_text)
            phone = extract_phone(p_text)
            role = extract_role(p)
            
            # Only create contact if we have at least one identifying piece of information
            if name or email or phone:
                contact = {
                    'organization': organization,
                    'person_name': name,
                    'role': role,
                    'email': email,
                    'phone': phone,
                    'source_url': source_url
                }
                contacts.append(contact)
    
    return contacts

def _extract_contacts_from_lists(soup, organization, source_url):
    """Extract contacts from list items that might contain contact information"""
    contacts = []
    
    # Look for lists that might contain contact information
    for ul in soup.find_all(["ul", "ol"]):
        # Check if parent or the list itself has contact-related classes or IDs
        parent_text = str(ul.parent.get('class', '')) + str(ul.parent.get('id', '')) + str(ul.get('class', '')) + str(ul.get('id', ''))
        if any(keyword in parent_text.lower() for keyword in ['contact', 'team', 'staff', 'directory', 'people']):
            for li in ul.find_all("li"):
                li_text = li.get_text()
                
                # Skip very short list items
                if len(li_text) < 10:
                    continue
                
                name = extract_name(li)
                email = extract_email(li_text)
                phone = extract_phone(li_text)
                role = extract_role(li)
                
                # Only create contact if we have at least one identifying piece of information
                if name or email or phone:
                    contact = {
                        'organization': organization,
                        'person_name': name,
                        'role': role,
                        'email': email,
                        'phone': phone,
                        'source_url': source_url
                    }
                    contacts.append(contact)
    
    return contacts

def extract_text(element):
    """Extract and clean text from a BeautifulSoup element"""
    if element:
        return element.get_text(strip=True)
    return ''

def extract_organization(soup, url):
    """Extract organization name from the page"""
    # Try common locations for organization name
    organization = ''
    
    # Try the title
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        organization = title.split('-')[0].split('|')[0].strip()
    
    # Try logo alt text
    if not organization:
        logo = soup.find('img', class_=lambda c: c and ('logo' in c.lower()))
        if logo and logo.get('alt'):
            organization = logo['alt']
    
    # If still not found, use domain from URL
    if not organization:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        organization = domain.replace('www.', '').split('.')[0].title()
        
    return organization

def extract_name(element):
    """Extract person name from an element"""
    # Look for elements that might contain names
    name_candidates = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
    for candidate in name_candidates:
        text = candidate.get_text(strip=True)
        # Basic heuristic: names are usually short (2-4 words)
        words = text.split()
        if 1 < len(words) < 5 and not any(char.isdigit() for char in text):
            return text
    
    # If no structured element found, try regex on the element's text
    text = element.get_text()
    name_patterns = [
        r'(?:Mr|Mrs|Ms|Dr|Prof|Sir|Madam|Tuan|Puan|Encik|Cik|Datuk|Dato\'|Tan Sri|Pn)\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ''

def extract_role(element):
    """Extract person role/position from an element"""
    text = element.get_text()
    
    # Common titles in Malaysia
    role_patterns = [
        r'(?:CEO|Chief Executive Officer|Managing Director|Director|Manager|Head of|Dean|Professor|Lecturer|Administrator|Secretary|Officer|Executive|Supervisor|Coordinator|Consultant|Specialist)',
        r'(?:Ketua|Pengarah|Pengurus|Penyelaras|Pegawai|Eksekutif|Setiausaha|Penasihat)',
    ]
    
    for pattern in role_patterns:
        match = re.search(f'{pattern}\\s+(?:of|for)?\\s+[\\w\\s]+', text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    # Look for role in smaller text or spans often used for titles
    small_texts = element.find_all(['small', 'span', 'div'], class_=lambda c: c and ('title' in str(c).lower() or 'role' in str(c).lower() or 'position' in str(c).lower()))
    for small in small_texts:
        small_text = small.get_text(strip=True)
        if small_text and len(small_text.split()) < 6:  # Job titles are usually brief
            return small_text
    
    return ''

def extract_email(text):
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ''

def extract_phone(text):
    """Extract phone numbers from text"""
    # Malaysian phone patterns
    phone_patterns = [
        r'\+?6?01\d[ -]?\d{3}[ -]?\d{4}',  # Mobile: +60123456789 or 0123456789
        r'\+?6?0\d[ -]?\d{7,8}',  # Landline: +6031234567 or 031234567
        r'\+?6?0\d{1,2}[ -]?\d{3}[ -]?\d{4}'  # Various formats
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    
    return ''

def get_all_links(html, base_url, domain_limit=True):
    """
    Extracts all links from an HTML page with option to limit to the same domain.
    
    Args:
        html (str): HTML content of the page
        base_url (str): The base URL for resolving relative links
        domain_limit (bool): Whether to limit links to the same domain
        
    Returns:
        list: List of URLs
    """
    if not html:
        return []
    
    from urllib.parse import urlparse
    base_domain = urlparse(base_url).netloc
    
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    # Find relevant pages that might contain contact information
    relevant_keywords = ['contact', 'about', 'team', 'staff', 'faculty', 'directory', 
                        'people', 'management', 'board', 'leadership', 'hubungi', 
                        'kakitangan', 'pengurusan', 'pegawai']
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        
        # Skip non-HTTP links, anchors, and javascript
        if not (full_url.startswith('http') or full_url.startswith('https')):
            continue
        
        # Apply domain limit if requested
        if domain_limit:
            url_domain = urlparse(full_url).netloc
            if url_domain != base_domain:
                continue
        
        # Prioritize pages that likely contain contact information
        link_text = a_tag.get_text().lower()
        
        # Check if URL or link text contains relevant keywords
        is_relevant = any(keyword in full_url.lower() or keyword in link_text for keyword in relevant_keywords)
        
        links.append((full_url, is_relevant))
    
    # Sort links by relevance (relevant ones first)
    links.sort(key=lambda x: not x[1])
    
    return [link for link, _ in links]

def save_to_csv(data, filename="leads.csv", append=True):
    """
    Saves or appends data to a CSV file.
    
    Args:
        data (list): List of dictionaries containing lead data
        filename (str): Name of the CSV file
        append (bool): Whether to append to existing file
        
    Returns:
        int: Number of records saved
    """
    if not data:
        logger.warning("No data to save")
        return 0
    
    mode = 'a' if append and os.path.exists(filename) else 'w'
    file_exists = os.path.exists(filename)
    
    fieldnames = ['organization', 'person_name', 'role', 'email', 'phone', 'source_url']
    
    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists or mode == 'w':
            writer.writeheader()
        
        for contact in data:
            # Filter out blank or almost blank records
            non_blank_fields = sum(1 for field in ['person_name', 'email', 'phone'] if contact.get(field))
            if non_blank_fields > 0:  # At least one identifying field must be present
                writer.writerow(contact)
    
    logger.info(f"Saved {len(data)} leads to {filename}")
    return len(data) 