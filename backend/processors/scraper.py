#!/usr/bin/env python3

"""
eCFR Scraper integrated into the backend.
This module handles fetching data from the eCFR API and website.
"""

import os
import re
import time
import json
import requests
import hashlib
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import concurrent.futures
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ecfr_scraper')

@dataclass
class ECFRTitle:
    """Represents a title from the eCFR API."""
    number: int
    name: str
    reserved: bool = False
    up_to_date_as_of: Optional[str] = None
    latest_amended_on: Optional[str] = None
    latest_issue_date: Optional[str] = None

@dataclass
class ECFRSection:
    """Represents a section from the eCFR API."""
    identifier: str
    title: str
    label: str = ""
    parent_identifier: Optional[str] = None
    html_url: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    children: List['ECFRSection'] = field(default_factory=list)

class ECFRScraper:
    """Scraper for the Electronic Code of Federal Regulations using the API."""
    
    BASE_URL = "https://www.ecfr.gov"
    API_URL = f"{BASE_URL}/api/versioner/v1"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    DELAY = 1.0  # Delay between requests in seconds (reasonable to avoid server strain)
    MAX_RETRIES = 3  # Maximum number of retries for each request
    RETRY_DELAY = 5.0  # Delay between retries in seconds
    
    def __init__(self, output_dir: str):
        """Initialize the scraper with output directories."""
        
        self.output_dir = output_dir
        self.formatted_dir = os.path.join(output_dir, "formatted")
        self.plain_dir = os.path.join(output_dir, "plain")
        
        # Create output directories if they don't exist
        os.makedirs(self.formatted_dir, exist_ok=True)
        os.makedirs(self.plain_dir, exist_ok=True)
        
        # Set up cache directory
        self.cache_dir = os.path.join(output_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Create a session for reuse
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
        # Track hierarchy for better organization
        self.current_hierarchy = {}
    
    def fetch_api(self, endpoint: str) -> Any:
        """Fetch data from the API with retries for rate limiting."""
        
        url = f"{self.API_URL}/{endpoint}"
        logger.info(f"Fetching API: {url}")
        
        # Check cache if available
        if hasattr(self, 'cache_dir'):
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Return from cache if it exists
            if os.path.exists(cache_file):
                logger.info(f"Loading from cache: {url}")
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load from cache: {e}")
                    # Continue with regular fetch if cache load fails
        
        # Use session if available
        request_func = self.session.get if hasattr(self, 'session') else requests.get
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Add reasonable delay before requests
                if attempt > 0:
                    # Exponential backoff for retries
                    retry_sleep = self.RETRY_DELAY * (2 ** (attempt - 1))
                    logger.info(f"Retry attempt {attempt+1}/{self.MAX_RETRIES}. Waiting {retry_sleep} seconds...")
                    time.sleep(retry_sleep)
                else:
                    time.sleep(self.DELAY)  # Standard delay for first attempt
                
                response = request_func(url, headers=self.HEADERS, timeout=30)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', self.RETRY_DELAY))
                    logger.warning(f"Rate limited! Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                # Save to cache if we have a cache directory
                if hasattr(self, 'cache_dir'):
                    try:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f)
                    except Exception as e:
                        logger.warning(f"Failed to write to cache: {e}")
                
                return data
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429 and attempt < self.MAX_RETRIES - 1:
                    continue  # Retry for rate limiting
                logger.error(f"HTTP Error fetching API {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    continue
                raise
            except Exception as e:
                logger.error(f"Error fetching API {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    continue
                raise
    
    def fetch_web_page(self, url: str) -> str:
        """Fetch a web page with retries for rate limiting."""
        
        logger.info(f"Fetching web page: {url}")
        
        # Check cache if available
        if hasattr(self, 'cache_dir'):
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.html")
            
            # Return from cache if it exists
            if os.path.exists(cache_file):
                logger.info(f"Loading from cache: {url}")
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    logger.warning(f"Failed to load from cache: {e}")
                    # Continue with regular fetch if cache load fails
        
        # Use session if available
        request_func = self.session.get if hasattr(self, 'session') else requests.get
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Add reasonable delay before requests
                if attempt > 0:
                    # Exponential backoff for retries
                    retry_sleep = self.RETRY_DELAY * (2 ** (attempt - 1))
                    logger.info(f"Retry attempt {attempt+1}/{self.MAX_RETRIES}. Waiting {retry_sleep} seconds...")
                    time.sleep(retry_sleep)
                else:
                    time.sleep(self.DELAY)  # Standard delay for first attempt
                
                response = request_func(url, headers=self.HEADERS, timeout=30)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', self.RETRY_DELAY))
                    logger.warning(f"Rate limited! Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                html_content = response.text
                
                # Save to cache if we have a cache directory
                if hasattr(self, 'cache_dir'):
                    try:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                    except Exception as e:
                        logger.warning(f"Failed to write to cache: {e}")
                
                return html_content
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429 and attempt < self.MAX_RETRIES - 1:
                    continue  # Retry for rate limiting
                logger.error(f"HTTP Error fetching web page {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    continue
                raise
            except Exception as e:
                logger.error(f"Error fetching web page {url}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    continue
                raise
    
    def get_all_titles(self) -> List[ECFRTitle]:
        """Get all titles from the eCFR API."""
        data = self.fetch_api("titles")
        titles = []
        
        if 'titles' in data:
            for title_data in data['titles']:
                if not title_data.get('reserved', False):
                    title = ECFRTitle(
                        number=title_data.get('number'),
                        name=title_data.get('name'),
                        reserved=title_data.get('reserved', False),
                        up_to_date_as_of=title_data.get('up_to_date_as_of'),
                        latest_amended_on=title_data.get('latest_amended_on'),
                        latest_issue_date=title_data.get('latest_issue_date')
                    )
                    titles.append(title)
        
        return titles
    
    def get_title_structure(self, title_number: int) -> List[Dict[str, Any]]:
        """Get the structure of a title."""
        url = f"{self.BASE_URL}/current/title-{title_number}"
        html_content = self.fetch_web_page(url)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        structure = []
        
        # Find main content area
        main_content = soup.find('main', id='main-content')
        if not main_content:
            main_content = soup.find('div', class_='main-content')
        if not main_content:
            main_content = soup.body
            
        if not main_content:
            logger.warning(f"Could not find main content for title {title_number}")
            return structure
        
        # Try to find agency information for this title
        agency_info = None
        agency_elements = main_content.find_all(['div', 'p', 'h3', 'h4'], 
                                              string=lambda s: s and ('agency' in s.lower() or 'department' in s.lower()))
        
        for element in agency_elements:
            text = element.get_text(strip=True)
            # Extract agency name
            if ':' in text:
                agency_info = text.split(':', 1)[1].strip()
            else:
                agency_info = text
            break
        
        # Look for tables - they often contain the primary structure
        tables = main_content.find_all('table')
        for table in tables:
            for link in table.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Skip empty or non-content links
                if not text or '#' in href or 'javascript' in href:
                    continue
                
                # Complete the URL if it's a relative path
                if not href.startswith('http'):
                    href = self.BASE_URL + href if href.startswith('/') else f"{self.BASE_URL}/{href}"
                
                # Create a unique identifier
                identifier = f"title-{title_number}-{href.split('/')[-1]}"
                
                item = {
                    'identifier': identifier,
                    'title': text,
                    'html_url': href,
                    'children': []
                }
                
                # Add agency if found
                if agency_info:
                    item['agency'] = agency_info
                
                structure.append(item)
        
        # If no tables or no links found in tables, look for links in divs
        if not structure:
            # Find divs that might contain structure (try various class patterns)
            potential_containers = main_content.find_all(['div', 'ul', 'ol'], 
                class_=lambda c: c and any(term in str(c).lower() for term in ['browse', 'toc', 'content', 'nav', 'menu']))
            
            for container in potential_containers:
                for link in container.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True)
                    
                    # Skip empty or non-content links
                    if not text or '#' in href or 'javascript' in href:
                        continue
                    
                    # Complete the URL if it's a relative path
                    if not href.startswith('http'):
                        href = self.BASE_URL + href if href.startswith('/') else f"{self.BASE_URL}/{href}"
                    
                    # Create a unique identifier
                    identifier = f"title-{title_number}-{href.split('/')[-1]}"
                    
                    item = {
                        'identifier': identifier,
                        'title': text,
                        'html_url': href,
                        'children': []
                    }
                    
                    # Add agency if found
                    if agency_info:
                        item['agency'] = agency_info
                    
                    structure.append(item)
        
        # If still no structure, grab all links from main content
        if not structure:
            for link in main_content.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Skip empty or non-content links
                if not text or '#' in href or 'javascript' in href:
                    continue
                
                # Skip links to other titles or the homepage
                if any(term in href.lower() for term in ['/title-', 'index.html', 'home']):
                    continue
                
                # Complete the URL if it's a relative path
                if not href.startswith('http'):
                    href = self.BASE_URL + href if href.startswith('/') else f"{self.BASE_URL}/{href}"
                
                # Create a unique identifier
                identifier = f"title-{title_number}-{href.split('/')[-1]}"
                
                item = {
                    'identifier': identifier,
                    'title': text,
                    'html_url': href,
                    'children': []
                }
                
                # Add agency if found
                if agency_info:
                    item['agency'] = agency_info
                
                structure.append(item)
        
        return structure
    
    def get_section_content(self, url: str, identifier: str) -> Dict[str, Any]:
        """Scrape content from a given URL."""
        try:
            html_content = self.fetch_web_page(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find main content
            main_content = soup.find('main', id='main-content')
            if not main_content:
                main_content = soup.find('div', class_='main-content')
            if not main_content:
                main_content = soup.find('div', id=lambda i: i and ('content' in i.lower()))
            if not main_content:
                main_content = soup.find('div', class_=lambda c: c and ('content' in c.lower()))
            if not main_content:
                main_content = soup.body
            
            if not main_content:
                logger.warning(f"Could not find main content for URL: {url}")
                return {
                    'identifier': identifier,
                    'title': url.split('/')[-1].replace('-', ' ').title(),
                    'html_content': "",
                    'text_content': ""
                }
            
            # Clean up content
            for element in main_content.select('.navigation, .search, .header, .footer, nav, script, style, .menu, .sidebar, .pagination'):
                element.decompose()
            
            # Get title
            title = ""
            # Try to find title in h1/h2 elements first
            title_elem = soup.find(['h1', 'h2'], id=lambda i: i and ('title' in i.lower() or 'heading' in i.lower()))
            if not title_elem:
                title_elem = soup.find(['h1', 'h2'], class_=lambda c: c and ('title' in c.lower() or 'heading' in c.lower()))
            if not title_elem:
                # Just take the first h1 or h2
                title_elem = soup.find(['h1', 'h2'])
            
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Fallback: use the last part of the URL as title
                title = url.split('/')[-1].replace('-', ' ').title()
            
            # Clean up the title
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Extract text content
            text_content = self.extract_plain_text(str(main_content))
            
            return {
                'identifier': identifier,
                'title': title,
                'html_content': str(main_content),
                'text_content': text_content,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error scraping content from URL {url}: {e}")
            return {
                'identifier': identifier,
                'title': url.split('/')[-1].replace('-', ' ').title(),
                'html_content': "",
                'text_content': "",
                'url': url,
                'error': str(e)
            }
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and convert to markdown."""
        if not html_content:
            return ""
        
        # Clean up common issues
        html_content = re.sub(r'<!\-\-.*?\-\->', '', html_content, flags=re.DOTALL)  # Remove comments
        html_content = re.sub(r'\s+', ' ', html_content)  # Normalize whitespace
        html_content = re.sub(r'<br\s*/?>', '\n', html_content)  # Convert <br> to newlines
        
        # Replace div with heading classes to actual headings
        for i in range(1, 7):
            html_content = re.sub(f'<div[^>]*?class=["\']h{i}["\'][^>]*?>(.*?)</div>', f'<h{i}>\\1</h{i}>', html_content)
        
        # Convert to markdown
        try:
            from html2text import HTML2Text
            h2t = HTML2Text()
            h2t.body_width = 0  # No wrapping
            h2t.inline_links = True
            h2t.unicode_snob = True
            md_content = h2t.handle(html_content)
        except ImportError:
            # Fallback to basic conversion
            soup = BeautifulSoup(html_content, 'html.parser')
            md_content = soup.get_text(separator='\n\n', strip=True)
        
        # Clean up markdown
        md_content = re.sub(r'\n{3,}', '\n\n', md_content)  # Remove excess newlines
        md_content = re.sub(r'!?\[\]\((?:javascript|data):.*?\)', '', md_content)  # Remove problematic links
        
        return md_content.strip()
    
    def extract_plain_text(self, html_content: str) -> str:
        """Extract plain text from HTML content."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'(\. )', '.\n', text)  # Add newlines after periods
        
        return text.strip()
    
    def create_safe_filename(self, text: str, max_length: int = 100) -> str:
        """Create a safe filename from text."""
        # Remove non-alphanumeric characters
        safe_text = re.sub(r'[^\w\s-]', '', text)
        # Replace whitespace with underscores
        safe_text = re.sub(r'[\s-]+', '_', safe_text).strip('_')
        # Truncate to max length
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
        
        return safe_text
    
    def save_document(self, title: str, identifier: str, html_content: str, url: str, 
                    path_prefix: str = "", hierarchy: List[str] = None) -> str:
        """Save a document's content to files with proper directory structure."""
        # Generate formatted and plain content
        formatted_content = self.clean_html_content(html_content)
        plain_content = self.extract_plain_text(html_content)
        
        # Create a safe filename
        safe_title = self.create_safe_filename(title)
        
        # Extract title number from identifier if available
        title_number = None
        if identifier and identifier.startswith('title-'):
            title_parts = identifier.split('-')
            if len(title_parts) > 1 and title_parts[1].isdigit():
                title_number = title_parts[1]
        
        # Create simplified directory structure based on title number
        formatted_subdir = ""
        plain_subdir = ""
        
        if title_number:
            # Create title-based directory
            title_dir = f"Title_{title_number}"
            
            # Create directories if they don't exist
            formatted_subdir = os.path.join(self.formatted_dir, title_dir)
            plain_subdir = os.path.join(self.plain_dir, title_dir)
            
            os.makedirs(formatted_subdir, exist_ok=True)
            os.makedirs(plain_subdir, exist_ok=True)
        else:
            formatted_subdir = self.formatted_dir
            plain_subdir = self.plain_dir
            
            # Add title prefix if provided
            if path_prefix:
                safe_title = f"{path_prefix}_{safe_title}"
        
        # Save formatted version
        formatted_path = os.path.join(formatted_subdir, f"{safe_title}.md")
        with open(formatted_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"Source: {url}\n")
            f.write(f"Identifier: {identifier}\n\n")
            
            # Add hierarchy information
            if hierarchy:
                f.write("## Hierarchy\n\n")
                for i, level in enumerate(hierarchy):
                    f.write(f"{'  ' * i}* {level}\n")
                f.write("\n")
                
            f.write(formatted_content)
        
        # Save plain version
        plain_path = os.path.join(plain_subdir, f"{safe_title}.txt")
        with open(plain_path, 'w', encoding='utf-8') as f:
            f.write(plain_content)
        
        # Create a relative path for logging
        rel_path = os.path.relpath(formatted_path, self.formatted_dir)
        logger.info(f"Saved document: {rel_path}")
        
        return safe_title
    
    def process_title(self, title_number: int) -> Dict[str, Any]:
        """Process a title and return the data."""
        try:
            # Get the titles list from API
            data = self.fetch_api("titles")
            
            # Find the specific title
            title_obj = None
            if 'titles' in data:
                for title_data in data['titles']:
                    if title_data.get('number') == title_number:
                        title_obj = ECFRTitle(
                            number=title_data.get('number'),
                            name=title_data.get('name'),
                            reserved=title_data.get('reserved', False),
                            up_to_date_as_of=title_data.get('up_to_date_as_of'),
                            latest_amended_on=title_data.get('latest_amended_on'),
                            latest_issue_date=title_data.get('latest_issue_date')
                        )
                        break
            
            if not title_obj:
                logger.error(f"Title {title_number} not found")
                return {"success": False, "error": f"Title {title_number} not found"}
            
            logger.info(f"Processing title {title_obj.number}: {title_obj.name}")
            
            # Get the title structure
            structure = self.get_title_structure(title_number)
            
            # Process the title content
            title_url = f"{self.BASE_URL}/current/title-{title_number}"
            title_content = self.get_section_content(title_url, f"title-{title_number}")
            
            # Save title content
            if title_content and title_content.get('html_content'):
                title_path = self.save_document(
                    title=f"Title {title_number}: {title_obj.name}",
                    identifier=f"title-{title_number}",
                    html_content=title_content.get('html_content', ''),
                    url=title_url,
                    hierarchy=[f"Title {title_number}: {title_obj.name}"]
                )
            
            # Process each section in the structure
            sections = []
            for item in structure:
                item_identifier = item.get('identifier')
                item_title = item.get('title', '')
                item_url = item.get('html_url', '')
                
                if not item_identifier or not item_url:
                    continue
                
                # Get section content
                section_content = self.get_section_content(item_url, item_identifier)
                
                # Skip if no content was found
                if not section_content or not section_content.get('html_content'):
                    continue
                
                # Save the document
                self.save_document(
                    title=item_title,
                    identifier=item_identifier,
                    html_content=section_content.get('html_content', ''),
                    url=item_url,
                    hierarchy=[f"Title {title_number}: {title_obj.name}", item_title]
                )
                
                # Add to sections
                sections.append({
                    'identifier': item_identifier,
                    'title': item_title,
                    'url': item_url,
                    'text_content': section_content.get('text_content', '')
                })
            
            # Return success data
            return {
                "success": True,
                "title": {
                    "number": title_obj.number,
                    "name": title_obj.name,
                    "up_to_date_as_of": title_obj.up_to_date_as_of,
                    "latest_amended_on": title_obj.latest_amended_on,
                    "latest_issue_date": title_obj.latest_issue_date
                },
                "sections_count": len(sections),
                "sections": sections
            }
            
        except Exception as e:
            logger.error(f"Error processing title {title_number}: {e}")
            return {"success": False, "error": str(e)}

def scrape_title(title_number: int, output_dir: str = "./data") -> Dict[str, Any]:
    """Scrape a single title and return the data."""
    scraper = ECFRScraper(output_dir)
    return scraper.process_title(title_number)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape a title from the eCFR")
    parser.add_argument("title_number", type=int, help="The title number to scrape")
    parser.add_argument("--output-dir", type=str, default="./data", help="Output directory")
    
    args = parser.parse_args()
    
    result = scrape_title(args.title_number, args.output_dir)
    
    if result.get("success", False):
        print(f"Successfully scraped Title {args.title_number} with {result.get('sections_count', 0)} sections")
    else:
        print(f"Failed to scrape Title {args.title_number}: {result.get('error')}")