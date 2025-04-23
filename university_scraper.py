from lead_generator.agents.scraper import fetch_page, save_to_csv, get_all_links
import logging
import time
import random
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger('lead_generator.university')

class UniversityScraper:
    """Specialized scraper for university staff directories"""
    
    def __init__(self, output_file="leads_university.csv"):
        self.output_file = output_file
        self.visited_urls = set()
        
    def scrape_university(self, base_url, max_pages=30, max_depth=3, delay_range=(2, 5)):
        """
        Scrape a university website for faculty/staff contact information
        
        Args:
            base_url (str): Base URL of the university website
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
        
        logger.info(f"Starting to scrape university website: {base_url}")
        
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
            contacts = self._parse_university_contacts(html, current_url)
            
            # Save the leads
            if contacts:
                num_saved = save_to_csv(contacts, self.output_file)
                total_leads += num_saved
                logger.info(f"Found {num_saved} leads on {current_url}")
                
            # If we haven't reached max depth, get more links
            if current_depth < max_depth:
                # Get all links from the page
                links = get_all_links(html, current_url, domain_limit=True)
                
                # Filter for relevant faculty/staff pages
                relevant_links = self._filter_university_links(links, base_url)
                
                # Add new URLs to visit
                for link in relevant_links:
                    if link not in self.visited_urls:
                        urls_to_visit.append((link, current_depth + 1))
                        
            # Add random delay
            time.sleep(random.uniform(*delay_range))
            
        logger.info(f"Completed scraping {base_url}. Total leads: {total_leads}")
        return total_leads
        
    def _filter_university_links(self, links, base_url):
        """Filter links that are likely to contain faculty/staff information"""
        relevant_keywords = [
            'staff', 'faculty', 'lecturer', 'academic', 'directory',
            'department', 'school', 'people', 'profile', 'contact',
            'professor', 'dean', 'head', 'management', 'team',
            'pensyarah', 'kakitangan', 'akademik', 'staf', 'jabatan',
            'fakulti', 'fakulta'
        ]
        
        filtered_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            link_domain = urlparse(link).netloc
            
            # Ensure we stay on the same domain
            if link_domain != base_domain:
                continue
                
            # Check if URL contains relevant keywords
            if any(keyword in link.lower() for keyword in relevant_keywords):
                filtered_links.append(link)
                continue
                
        # Prioritize most relevant links first
        sorted_links = sorted(filtered_links, 
                             key=lambda x: not any(keyword in x.lower() for keyword in relevant_keywords))
        
        # Limit the number of links to avoid excessive crawling
        return sorted_links[:30]
        
    def _parse_university_contacts(self, html, source_url):
        """Parse contacts from a university website"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        contacts = []
        
        # Extract university name
        university = self._extract_university_name(soup, source_url)
        department = self._extract_department_name(soup, source_url)
        
        # Combine university and department for organization field
        organization = f"{university}{' - ' + department if department else ''}"
        
        # Try different parsing strategies
        
        # Strategy 1: Parse staff directory tables
        table_contacts = self._extract_contacts_from_tables(soup, organization, source_url)
        contacts.extend(table_contacts)
        
        # Strategy 2: Parse staff profile cards/sections
        profile_contacts = self._extract_contacts_from_profiles(soup, organization, source_url)
        contacts.extend(profile_contacts)
        
        # Strategy 3: Parse contact sections with less structure
        section_contacts = self._extract_contacts_from_sections(soup, organization, source_url)
        contacts.extend(section_contacts)
        
        return contacts
        
    def _extract_university_name(self, soup, source_url):
        """Extract university name from the page"""
        # Try to find the university name in the header
        for header_tag in ['h1', 'h2', 'h3']:
            header = soup.find(header_tag, class_=lambda c: c and ('site-title' in str(c) or 'logo-text' in str(c)))
            if header:
                return header.get_text(strip=True)
        
        # Try the title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Universities often use a standard format like "PageName | UniversityName"
            for separator in ['-', '|', '«', '»', '::']:
                if separator in title:
                    parts = title.split(separator)
                    return parts[-1].strip()  # Usually university name is at the end
            
        # Check meta tags
        meta_org = soup.find('meta', property=['og:site_name', 'og:title'])
        if meta_org and meta_org.get('content'):
            return meta_org['content']
        
        # Extract from URL if all else fails
        domain = urlparse(source_url).netloc
        if 'edu.my' in domain:
            parts = domain.split('.')
            if len(parts) >= 3:
                return parts[0].upper()
        
        return domain.replace('www.', '').split('.')[0].upper()
    
    def _extract_department_name(self, soup, source_url):
        """Extract department/faculty name from the page"""
        # Look for department heading
        department_headings = soup.find_all(['h1', 'h2', 'h3'], string=lambda s: s and any(keyword in s.lower() for keyword in ['faculty', 'department', 'school', 'fakulti', 'jabatan']))
        if department_headings:
            return department_headings[0].get_text(strip=True)
        
        # Check breadcrumbs
        breadcrumbs = soup.find(['nav', 'div'], class_=lambda c: c and 'breadcrumb' in str(c))
        if breadcrumbs:
            items = breadcrumbs.find_all('li')
            # Department is usually the second or third item
            if len(items) > 2:
                return items[-2].get_text(strip=True)
        
        # Check URL path for department info
        path = urlparse(source_url).path
        path_parts = [p for p in path.split('/') if p]
        dept_keywords = ['faculty', 'department', 'school', 'fakulti', 'jabatan', 'fac']
        for part in path_parts:
            if any(keyword in part.lower() for keyword in dept_keywords):
                return part.replace('-', ' ').replace('_', ' ').title()
        
        return ''
    
    def _extract_contacts_from_tables(self, soup, organization, source_url):
        """Extract contacts from staff directory tables"""
        contacts = []
        tables = soup.find_all('table')
        
        for table in tables:
            # Look for tables with relevant class names or IDs
            if table.get('class') and any(c in ' '.join(table['class']).lower() for c in ['staff', 'directory', 'faculty', 'lecturer']):
                pass  # Definitely a staff table
            elif table.get('id') and any(c in table['id'].lower() for c in ['staff', 'directory', 'faculty', 'lecturer']):
                pass  # Definitely a staff table
            elif not (any(th for th in table.find_all('th'))):
                # Skip tables without headers, less likely to be staff directories
                continue
            
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
                    if any(keyword in text for keyword in ['name', 'nama', 'staff', 'lecturer']):
                        name_col = i
                    elif any(keyword in text for keyword in ['position', 'jawatan', 'role', 'title', 'designation']):
                        role_col = i
                    elif any(keyword in text for keyword in ['email', 'e-mail', 'emel']):
                        email_col = i
                    elif any(keyword in text for keyword in ['phone', 'tel', 'telefon', 'contact']):
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
                    # Try to find email links
                    email_link = cells[email_col].find('a', href=lambda h: h and 'mailto:' in h)
                    if email_link:
                        email = email_link['href'].replace('mailto:', '').split('?')[0]
                    else:
                        email = self._extract_email(cells[email_col].get_text())
                else:
                    # Try to find email in any cell
                    for cell in cells:
                        email_link = cell.find('a', href=lambda h: h and 'mailto:' in h)
                        if email_link:
                            email = email_link['href'].replace('mailto:', '').split('?')[0]
                            break
                        
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
                
                # Clean up the name (sometimes includes titles)
                person_name = re.sub(r'^(Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.|Assoc\.|Asst\.)\s+', '', person_name).strip()
                
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
    
    def _extract_contacts_from_profiles(self, soup, organization, source_url):
        """Extract contacts from faculty/staff profile cards or sections"""
        contacts = []
        
        # Look for common profile containers
        profile_containers = soup.find_all(['div', 'article', 'section', 'li'], 
                                        class_=lambda c: c and any(keyword in str(c).lower() 
                                                                for keyword in ['profile', 'staff', 'faculty', 'person', 'member', 'card', 'team']))
        
        for container in profile_containers:
            # Extract name (usually in a heading element)
            name_elem = container.find(['h2', 'h3', 'h4', 'h5', 'strong', 'b', 'a'], class_=lambda c: c and ('name' in str(c).lower() if c else False))
            if not name_elem:
                name_elem = container.find(['h2', 'h3', 'h4', 'h5', 'strong', 'b'])
            
            person_name = name_elem.get_text(strip=True) if name_elem else ''
            
            # Clean titles from name
            person_name = re.sub(r'^(Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.|Assoc\.|Asst\.)\s+', '', person_name).strip()
            
            if not person_name:
                continue  # Skip if no name found
            
            # Extract role
            role_elem = container.find(['p', 'div', 'span'], class_=lambda c: c and any(keyword in str(c).lower() 
                                                                           for keyword in ['title', 'role', 'position', 'designation', 'job']))
            role = role_elem.get_text(strip=True) if role_elem else ''
            
            if not role:
                # Try to find role in paragraphs or spans near the name
                siblings = name_elem.find_next_siblings(['p', 'span', 'div'])
                for sibling in siblings[:2]:  # Check the next couple elements
                    text = sibling.get_text(strip=True)
                    if text and len(text.split()) < 7:  # Roles are usually short phrases
                        role = text
                        break
            
            # Extract email
            email_elem = container.find('a', href=lambda h: h and 'mailto:' in h)
            if email_elem:
                email = email_elem['href'].replace('mailto:', '').split('?')[0]
            else:
                email = self._extract_email(container.get_text())
            
            # Extract phone
            phone_elem = container.find('a', href=lambda h: h and 'tel:' in h)
            if phone_elem:
                phone = phone_elem['href'].replace('tel:', '')
            else:
                phone = self._extract_phone(container.get_text())
            
            contacts.append({
                'organization': organization,
                'person_name': person_name,
                'role': role,
                'email': email,
                'phone': phone,
                'source_url': source_url
            })
        
        return contacts
    
    def _extract_contacts_from_sections(self, soup, organization, source_url):
        """Extract contacts from less structured sections"""
        contacts = []
        
        # Look for potential sections with contact info
        sections = soup.find_all(['section', 'div'], class_=lambda c: c and any(keyword in str(c).lower() for keyword in 
                                                                          ['contact', 'staff', 'faculty', 'people', 'team']))
        
        for section in sections:
            # Extract paragraphs that might contain contact info
            paragraphs = section.find_all(['p', 'div'], recursive=False)
            
            current_person = None
            current_role = None
            current_email = None
            current_phone = None
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Look for academic titles followed by names
                name_match = re.search(r'(Dr\.|Prof\.|Assoc\. Prof\.|Professor|Mr\.|Mrs\.|Ms\.)\s+([A-Z][a-zA-Z\s\'\.]+)', text)
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
                    current_person = name_match.group(2)
                    current_role = None
                    current_email = None
                    current_phone = None
                    continue
                
                # Extract email
                email = self._extract_email(text)
                if email:
                    current_email = email
                
                # Extract phone
                phone = self._extract_phone(text)
                if phone:
                    current_phone = phone
                
                # Check for role keywords
                role_keywords = ['professor', 'lecturer', 'dean', 'head', 'director', 'coordinator', 'chair', 'president']
                if current_person and not current_role and any(keyword in text.lower() for keyword in role_keywords):
                    current_role = text
            
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
    
    def _extract_email(self, text):
        """Extract email address from text"""
        # Handle obfuscated emails (common in university websites)
        text = text.replace(' [at] ', '@').replace(' (at) ', '@').replace('[dot]', '.').replace('(dot)', '.')
        
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
        
        # Look for formatted numbers with extensions
        ext_pattern = r'(\+?6?0\d[ -]?\d{7,8})(?:\s*(?:ext|ext\.|x|Ext)\.?\s*(\d{1,4}))?'
        ext_matches = re.findall(ext_pattern, text)
        if ext_matches:
            phone, ext = ext_matches[0]
            if ext:
                return f"{phone} Ext. {ext}"
            return phone
        
        return ''
    
    def scrape_multiple_universities(self, university_urls, max_pages_per_university=25, delay_between_universities=(10, 15)):
        """
        Scrape multiple university websites
        
        Args:
            university_urls (list): List of university website URLs
            max_pages_per_university (int): Maximum pages to scrape per university
            delay_between_universities (tuple): Range for random delay between universities
            
        Returns:
            int: Total number of leads collected
        """
        total_leads = 0
        
        for url in university_urls:
            leads = self.scrape_university(url, max_pages=max_pages_per_university)
            total_leads += leads
            
            # Add delay between universities
            if url != university_urls[-1]:  # Skip delay after the last university
                delay = random.uniform(*delay_between_universities)
                logger.info(f"Waiting {delay:.1f} seconds before next university...")
                time.sleep(delay)
        
        return total_leads 