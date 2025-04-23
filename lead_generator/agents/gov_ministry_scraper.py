from lead_generator.agents.scraper import fetch_page, save_to_csv, get_all_links
import logging
import time
import random
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger('lead_generator.gov_ministry')

class GovMinistryScraper:
    """Specialized scraper for Malaysian government ministry websites"""
    
    def __init__(self, output_file="leads_gov_ministry.csv"):
        self.output_file = output_file
        self.visited_urls = set()
        
    def scrape_ministry(self, base_url, max_pages=20, max_depth=2, delay_range=(3, 7)):
        """
        Scrape a government ministry website for contact information
        
        Args:
            base_url (str): Base URL of the ministry website
            max_pages (int): Maximum number of pages to scrape
            max_depth (int): Maximum link depth to follow
            delay_range (tuple): Range for random delay between requests
            
        Returns:
            int: Total number of leads collected
        """
        total_leads = 0
        page_count = 0
        urls_to_visit = [(base_url, 0)]  # (url, depth)
        self.visited_urls = set()
        
        logger.info(f"Starting to scrape ministry website: {base_url}")
        
        # Always try to scrape the contact page first if it exists
        contact_patterns = [
            '/contact', '/contact-us', '/hubungi', '/hubungi-kami', 
            '/about/contact', '/en/contact', '/ms/contact',
            '/en/about-us', '/en/about', '/ms/mengenai-kami'
        ]
        
        for pattern in contact_patterns:
            contact_url = f"{base_url}{pattern}"
            if contact_url not in self.visited_urls:
                urls_to_visit.insert(0, (contact_url, 0))  # Add to the beginning of the queue
        
        while urls_to_visit and page_count < max_pages:
            # Get the next URL and its depth
            current_url, current_depth = urls_to_visit.pop(0)
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
                
            # Mark as visited
            self.visited_urls.add(current_url)
            page_count += 1
            
            logger.info(f"Scraping page {page_count}/{max_pages}: {current_url}")
            
            # Fetch the page
            html = fetch_page(current_url)
            if not html:
                continue
                
            # Parse for contacts
            contacts = self._parse_ministry_contacts(html, current_url)
            
            # Save the leads
            if contacts:
                num_saved = save_to_csv(contacts, self.output_file)
                total_leads += num_saved
                logger.info(f"Found {num_saved} leads on {current_url}")
            else:
                logger.info(f"No leads found on {current_url}")
                
            # If we haven't reached max depth, get more links
            if current_depth < max_depth:
                # Get all links from the page
                links = get_all_links(html, current_url, domain_limit=True)
                
                # Filter for relevant contact/staff pages
                relevant_links = self._filter_relevant_links(links, base_url)
                
                # Log the links we're going to visit
                if relevant_links:
                    logger.debug(f"Found {len(relevant_links)} relevant links on {current_url}")
                
                # Add new URLs to visit
                for link in relevant_links:
                    if link not in self.visited_urls:
                        urls_to_visit.append((link, current_depth + 1))
                        
            # Add random delay
            time.sleep(random.uniform(*delay_range))
            
        logger.info(f"Completed scraping {base_url}. Total leads: {total_leads}")
        return total_leads
        
    def _filter_relevant_links(self, links, base_url):
        """Filter links that are likely to contain contact information"""
        relevant_keywords = [
            'contact', 'direktori', 'staff', 'pegawai', 'pengurusan',
            'management', 'organisation', 'organisasi', 'carta', 'chart',
            'about', 'tentang', 'warga', 'hubungi', 'board', 'lembaga',
            'pengarah', 'team', 'pasukan', 'directory', 'jabatan', 'info'
        ]
        
        # Additional ministry-specific keywords
        ministry_keywords = [
            'ketua-pengarah', 'menteri', 'kementerian', 'minister', 
            'timbalan', 'deputy', 'ministry', 'pejabat', 'office',
            'bahagian', 'division', 'unit', 'sektor', 'sector'
        ]
        
        filtered_links = []
        base_domain = urlparse(base_url).netloc
        
        # Add the following specific paths that often contain contact information
        specific_paths = [
            '/profile', '/about-us', '/about', '/contact', '/contact-us',
            '/about/contact', '/directory', '/organization', '/management',
            '/en/contact', '/ms/hubungi', '/en/about-us', '/ms/mengenai-kami',
            '/en/directory', '/ms/direktori', '/en/management', '/ms/pengurusan'
        ]
        
        for path in specific_paths:
            specific_url = f"{base_url}{path}"
            if specific_url not in filtered_links and specific_url not in self.visited_urls:
                filtered_links.append(specific_url)
        
        # Add other links based on relevance
        for link in links:
            link_domain = urlparse(link).netloc
            
            # Ensure we stay on the same domain
            if link_domain != base_domain:
                continue
                
            # Check if URL contains relevant keywords
            if any(keyword in link.lower() for keyword in relevant_keywords + ministry_keywords):
                if link not in filtered_links and link not in self.visited_urls:
                    filtered_links.append(link)
                    continue
                
        # Prioritize most relevant links first
        sorted_links = sorted(filtered_links, 
                             key=lambda x: not any(keyword in x.lower() for keyword in relevant_keywords))
        
        # Limit the number of links to avoid excessive crawling
        return sorted_links[:20]
        
    def _parse_ministry_contacts(self, html, source_url):
        """Parse contacts from a government ministry website"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        contacts = []
        
        # Extract organization name
        organization = self._extract_ministry_organization(soup, source_url)
        logger.info(f"Parsing contacts for organization: {organization} from {source_url}")
        
        # Try different parsing strategies
        
        # Strategy 1: Look for tables with contact information
        table_contacts = self._extract_contacts_from_tables(soup, organization, source_url)
        if table_contacts:
            logger.info(f"Found {len(table_contacts)} contacts in tables on {source_url}")
            contacts.extend(table_contacts)
        
        # Strategy 2: Look for structured staff/management listings
        staff_contacts = self._extract_contacts_from_staff_listing(soup, organization, source_url)
        if staff_contacts:
            logger.info(f"Found {len(staff_contacts)} contacts in staff listings on {source_url}")
            contacts.extend(staff_contacts)
        
        # Strategy 3: Look for contact info in contact sections
        section_contacts = self._extract_contacts_from_contact_sections(soup, organization, source_url)
        if section_contacts:
            logger.info(f"Found {len(section_contacts)} contacts in contact sections on {source_url}")
            contacts.extend(section_contacts)
        
        # Strategy 4: Try to extract contacts from paragraphs that contain contact-like information
        paragraph_contacts = self._extract_contacts_from_paragraphs(soup, organization, source_url)
        if paragraph_contacts:
            logger.info(f"Found {len(paragraph_contacts)} contacts in paragraphs on {source_url}")
            contacts.extend(paragraph_contacts)
        
        # Strategy 5: Look for contacts in list items
        list_contacts = self._extract_contacts_from_lists(soup, organization, source_url)
        if list_contacts:
            logger.info(f"Found {len(list_contacts)} contacts in list items on {source_url}")
            contacts.extend(list_contacts)
        
        # Final count
        if contacts:
            logger.info(f"Total of {len(contacts)} contacts extracted from {source_url}")
        else:
            logger.warning(f"No contacts found on {source_url}")
            
        return contacts
        
    def _extract_ministry_organization(self, soup, source_url):
        """Extract organization name from a ministry website"""
        # Try to find the organization name in the header/logo
        org_element = soup.find(['h1', 'h2'], class_=lambda c: c and ('site-title' in str(c) or 'logo-text' in str(c)))
        if org_element:
            return org_element.get_text(strip=True)
            
        # Try the title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Clean the title (remove typical suffixes)
            for separator in ['-', '|', '«', '»', '::']:
                if separator in title:
                    parts = title.split(separator)
                    return parts[0].strip()
            return title
            
        # Try meta tags
        meta_org = soup.find('meta', property='og:site_name')
        if meta_org and meta_org.get('content'):
            return meta_org['content']
            
        # Extract from URL if all else fails
        domain = urlparse(source_url).netloc
        if 'gov.my' in domain:
            parts = domain.split('.')
            if len(parts) >= 3:
                return parts[-3].upper()
                
        return domain.replace('www.', '').split('.')[0].upper()
        
    def _extract_contacts_from_tables(self, soup, organization, source_url):
        """Extract contacts from HTML tables"""
        contacts = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            header_row = rows[0] if rows else None
            
            # Try to identify column positions
            name_col = -1
            role_col = -1
            email_col = -1
            phone_col = -1
            
            if header_row:
                header_cells = header_row.find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    text = cell.get_text().lower()
                    if any(keyword in text for keyword in ['name', 'nama']):
                        name_col = i
                    elif any(keyword in text for keyword in ['position', 'jawatan', 'role', 'title']):
                        role_col = i
                    elif any(keyword in text for keyword in ['email', 'e-mail', 'emel']):
                        email_col = i
                    elif any(keyword in text for keyword in ['phone', 'tel', 'telefon']):
                        phone_col = i
            
            # Process data rows
            for row in rows[1:] if header_row else rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:  # Skip rows without enough cells
                    continue
                    
                # Extract data based on identified columns or positional assumptions
                person_name = ''
                role = ''
                email = ''
                phone = ''
                
                if name_col >= 0 and name_col < len(cells):
                    person_name = cells[name_col].get_text(strip=True)
                elif len(cells) > 0:  # Assume first column is name if not identified
                    person_name = cells[0].get_text(strip=True)
                    
                if role_col >= 0 and role_col < len(cells):
                    role = cells[role_col].get_text(strip=True)
                elif len(cells) > 1 and name_col != 1:  # Assume second column is role if not identified
                    role = cells[1].get_text(strip=True)
                    
                if email_col >= 0 and email_col < len(cells):
                    email = self._extract_email(cells[email_col].get_text())
                else:
                    # Try to find email in any cell
                    for cell in cells:
                        email = self._extract_email(cell.get_text())
                        if email:
                            break
                            
                if phone_col >= 0 and phone_col < len(cells):
                    phone = self._extract_phone(cells[phone_col].get_text())
                else:
                    # Try to find phone in any cell
                    for cell in cells:
                        phone = self._extract_phone(cell.get_text())
                        if phone:
                            break
                
                # Create contact entry if we have at least a name or role
                if person_name or role:
                    contacts.append({
                        'organization': organization,
                        'person_name': person_name,
                        'role': role,
                        'email': email,
                        'phone': phone,
                        'source_url': source_url
                    })
                    
        return contacts
        
    def _extract_contacts_from_staff_listing(self, soup, organization, source_url):
        """Extract contacts from structured staff/management listings"""
        contacts = []
        
        # Look for sections with staff listings
        staff_sections = soup.find_all(['div', 'section', 'ul'], class_=lambda c: c and any(keyword in str(c).lower() 
                                                                    for keyword in ['staff', 'team', 'management', 'pegawai', 'pengurusan', 'directory']))
        
        for section in staff_sections:
            # Look for individual staff entries
            entries = section.find_all(['div', 'li', 'article'], class_=lambda c: c and ('staff' in str(c).lower() or 'member' in str(c).lower() or 'profile' in str(c).lower()))
            
            # If no structured entries found, try list items
            if not entries and section.name == 'ul':
                entries = section.find_all('li')
                
            # If still no entries, try generic divs
            if not entries:
                entries = section.find_all(['div', 'p'], recursive=False)
                
            for entry in entries:
                # Extract name
                name_elem = entry.find(['h3', 'h4', 'h5', 'strong', 'b', 'span', 'div'], class_=lambda c: c and ('name' in str(c).lower() or 'nama' in str(c).lower()))
                person_name = name_elem.get_text(strip=True) if name_elem else ''
                
                # If no specific name element, try to extract from text
                if not person_name:
                    # Look for patterns like titles followed by names
                    text = entry.get_text()
                    name_matches = re.findall(r'(?:En|Encik|Puan|Cik|Dr|Prof|Tuan|Datin|Datuk|Dato\'|Tan Sri)\.\s+([A-Z][a-zA-Z\s\']+)', text)
                    if name_matches:
                        person_name = name_matches[0]
                        
                # Extract role
                role_elem = entry.find(['p', 'span', 'div'], class_=lambda c: c and ('role' in str(c).lower() or 'position' in str(c).lower() or 'jawatan' in str(c).lower()))
                role = role_elem.get_text(strip=True) if role_elem else ''
                
                # If no specific role element, try to extract from text
                if not role and person_name:
                    lines = [line.strip() for line in entry.get_text().split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if person_name in line and i+1 < len(lines):
                            role = lines[i+1]
                            break
                            
                # Extract email and phone
                email = self._extract_email(entry.get_text())
                phone = self._extract_phone(entry.get_text())
                
                # Look for email in mailto links
                email_link = entry.find('a', href=lambda h: h and h.startswith('mailto:'))
                if email_link and not email:
                    email = email_link['href'].replace('mailto:', '').split('?')[0]
                    
                # Look for phone in tel links
                phone_link = entry.find('a', href=lambda h: h and h.startswith('tel:'))
                if phone_link and not phone:
                    phone = phone_link['href'].replace('tel:', '')
                
                # Create contact entry if we have at least a name
                if person_name:
                    contacts.append({
                        'organization': organization,
                        'person_name': person_name,
                        'role': role,
                        'email': email,
                        'phone': phone,
                        'source_url': source_url
                    })
                    
        return contacts
        
    def _extract_contacts_from_contact_sections(self, soup, organization, source_url):
        """Extract contacts from contact sections without clear structure"""
        contacts = []
        
        # Look for contact sections
        contact_sections = soup.find_all(['div', 'section'], id=lambda i: i and 'contact' in i.lower())
        if not contact_sections:
            contact_sections = soup.find_all(['div', 'section'], class_=lambda c: c and 'contact' in str(c).lower())
            
        for section in contact_sections:
            # Extract all text with line breaks
            text_blocks = section.get_text().split('\n')
            
            current_person = None
            current_role = None
            current_email = None
            current_phone = None
            
            for line in text_blocks:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for name patterns
                name_match = re.search(r'(?:En|Encik|Puan|Cik|Dr|Prof|Tuan|Datin|Datuk|Dato\'|Tan Sri)\.\s+([A-Z][a-zA-Z\s\']+)', line)
                if name_match:
                    # If we found a new person, save the previous one
                    if current_person:
                        contacts.append({
                            'organization': organization,
                            'person_name': current_person,
                            'role': current_role or '',
                            'email': current_email or '',
                            'phone': current_phone or '',
                            'source_url': source_url
                        })
                        
                    # Start new person
                    current_person = name_match.group(1)
                    current_role = None
                    current_email = None
                    current_phone = None
                    continue
                    
                # Look for roles (typically short lines after a name)
                if current_person and not current_role and len(line.split()) < 6:
                    # Check if line contains common role keywords
                    role_keywords = ['manager', 'director', 'officer', 'head', 'pengurus', 'pengarah', 'ketua', 'pegawai']
                    if any(keyword in line.lower() for keyword in role_keywords):
                        current_role = line
                        continue
                        
                # Check for email
                email = self._extract_email(line)
                if email:
                    current_email = email
                    
                # Check for phone
                phone = self._extract_phone(line)
                if phone:
                    current_phone = phone
                    
            # Save the last person
            if current_person:
                contacts.append({
                    'organization': organization,
                    'person_name': current_person,
                    'role': current_role or '',
                    'email': current_email or '',
                    'phone': current_phone or '',
                    'source_url': source_url
                })
                
        return contacts
        
    def _extract_contacts_from_paragraphs(self, soup, organization, source_url):
        """Extract contacts from paragraphs that might contain contact information"""
        contacts = []
        
        # Look for paragraphs
        for p in soup.find_all('p'):
            p_text = p.get_text(strip=True)
            
            # Skip very short or empty paragraphs
            if len(p_text) < 10:
                continue
                
            # Check if paragraph contains contact indicators
            contact_indicators = ['@', 'email', 'e-mail', 'emel', 'phone', 'tel', 'telefon', 
                                 'contact', 'hubungi', 'officer', 'pegawai', 'manager', 'pengurus']
                                 
            if any(indicator in p_text.lower() for indicator in contact_indicators):
                # Try to extract a name
                name = ''
                name_match = re.search(r'(?:En|Encik|Puan|Cik|Dr|Prof|Tuan|Datin|Datuk|Dato\'|Tan Sri)\.\s+([A-Z][a-zA-Z\s\']+)', p_text)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    # Try to find a name pattern without title
                    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', p_text)
                    if name_match:
                        name = name_match.group(1).strip()
                
                # Extract email and phone
                email = self._extract_email(p_text)
                phone = self._extract_phone(p_text)
                
                # Extract role
                role = ''
                role_patterns = [
                    r'(?:Ketua|Pengarah|Pengurus|Setiausaha|Pegawai)\s+([A-Za-z\s]+)',
                    r'(?:Director|Manager|Officer|Secretary|Head)\s+(?:of\s+)?([A-Za-z\s]+)'
                ]
                
                for pattern in role_patterns:
                    role_match = re.search(pattern, p_text)
                    if role_match:
                        role = role_match.group(0).strip()
                        break
                
                # Create contact if we have at least some useful information
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
        
    def _extract_contacts_from_lists(self, soup, organization, source_url):
        """Extract contacts from list items that might contain contact information"""
        contacts = []
        
        # Look for list items
        for li in soup.find_all('li'):
            li_text = li.get_text(strip=True)
            
            # Skip very short list items
            if len(li_text) < 10:
                continue
                
            # Check if it contains contact indicators
            contact_indicators = ['@', 'email', 'e-mail', 'emel', 'phone', 'tel', 'telefon', 
                                 'contact', 'hubungi', 'officer', 'pegawai']
                                 
            if any(indicator in li_text.lower() for indicator in contact_indicators):
                # Try to extract information
                name = ''
                name_match = re.search(r'(?:En|Encik|Puan|Cik|Dr|Prof|Tuan|Datin|Datuk|Dato\'|Tan Sri)\.\s+([A-Z][a-zA-Z\s\']+)', li_text)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    # Try to find a name without title
                    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', li_text)
                    if name_match:
                        name = name_match.group(1).strip()
                
                # Extract email and phone
                email = self._extract_email(li_text)
                phone = self._extract_phone(li_text)
                
                # Create contact if we have at least some useful information
                if name or email or phone:
                    contact = {
                        'organization': organization,
                        'person_name': name,
                        'role': self._extract_role_from_text(li_text),
                        'email': email,
                        'phone': phone,
                        'source_url': source_url
                    }
                    contacts.append(contact)
        
        return contacts
    
    def _extract_role_from_text(self, text):
        """Extract role/position from text"""
        # Common role patterns
        role_patterns = [
            r'(?:Ketua|Pengarah|Pengurus|Setiausaha|Pegawai)\s+([A-Za-z\s]+)',
            r'(?:Director|Manager|Officer|Secretary|Head)\s+(?:of\s+)?([A-Za-z\s]+)',
            r'(?:Chief|Deputy|Assistant)\s+([A-Za-z\s]+)'
        ]
        
        for pattern in role_patterns:
            role_match = re.search(pattern, text)
            if role_match:
                return role_match.group(0).strip()
        
        return ''
        
    def _extract_email(self, text):
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ''
        
    def _extract_phone(self, text):
        """Extract phone number from text"""
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
                
        return ''
        
    def scrape_multiple_ministries(self, ministry_urls, max_pages_per_ministry=15, delay_between_ministries=(10, 20)):
        """
        Scrape multiple ministry websites
        
        Args:
            ministry_urls (list): List of ministry website URLs
            max_pages_per_ministry (int): Maximum pages to scrape per ministry
            delay_between_ministries (tuple): Range for random delay between ministries
            
        Returns:
            int: Total number of leads collected
        """
        total_leads = 0
        
        for url in ministry_urls:
            leads = self.scrape_ministry(url, max_pages=max_pages_per_ministry)
            total_leads += leads
            
            # Add delay between ministries
            if url != ministry_urls[-1]:  # Skip delay after the last ministry
                delay = random.uniform(*delay_between_ministries)
                logger.info(f"Waiting {delay:.1f} seconds before next ministry...")
                time.sleep(delay)
                
        return total_leads 