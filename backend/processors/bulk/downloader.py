#!/usr/bin/env python3

"""
Downloader for GovInfo Bulk XML eCFR data.
"""

import os
import time
import logging
import requests
from typing import Tuple

# Setup logging
logger = logging.getLogger('bulk_downloader')

# Constants
GOVINFO_BASE_URL = "https://www.govinfo.gov/bulkdata/ECFR"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
MAX_RETRIES = 3
RETRY_DELAY = 10
DELAY_BETWEEN_REQUESTS = 3  # Be nice to the server

# Known title names
TITLE_NAMES = {
    1: "General Provisions", 2: "Federal Financial Assistance", 3: "The President",
    4: "Accounts", 5: "Administrative Personnel", 6: "Domestic Security",
    7: "Agriculture", 8: "Aliens and Nationality", 9: "Animals and Animal Products",
    10: "Energy", 11: "Federal Elections", 12: "Banks and Banking",
    13: "Business Credit and Assistance", 14: "Aeronautics and Space",
    15: "Commerce and Foreign Trade", 16: "Commercial Practices",
    17: "Commodity and Securities Exchanges", 18: "Conservation of Power and Water Resources",
    19: "Customs Duties", 20: "Employees' Benefits", 21: "Food and Drugs",
    22: "Foreign Relations", 23: "Highways", 24: "Housing and Urban Development",
    25: "Indians", 26: "Internal Revenue", 27: "Alcohol, Tobacco Products and Firearms",
    28: "Judicial Administration", 29: "Labor", 30: "Mineral Resources",
    31: "Money and Finance: Treasury", 32: "National Defense",
    33: "Navigation and Navigable Waters", 34: "Education", 
    35: "Panama Canal", 36: "Parks, Forests, and Public Property",
    37: "Patents, Trademarks, and Copyrights", 38: "Pensions, Bonuses, and Veterans' Relief",
    39: "Postal Service", 40: "Protection of Environment",
    41: "Public Contracts and Property Management", 42: "Public Health",
    43: "Public Lands: Interior", 44: "Emergency Management and Assistance",
    45: "Public Welfare", 46: "Shipping", 47: "Telecommunication",
    48: "Federal Acquisition Regulations System", 49: "Transportation",
    50: "Wildlife and Fisheries"
}

def download_title(title_num: int, output_dir: str, skip_existing: bool = True) -> Tuple[bool, str, int]:
    """Download a specific title's XML data."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Define file path
    file_path = os.path.join(output_dir, f"title-{title_num}.xml")
    
    # Skip if already downloaded and skip_existing is True
    if skip_existing and os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        if file_size > 0:
            logger.info(f"Title {title_num} already downloaded ({file_size} bytes)")
            return True, file_path, file_size
    
    # Define the URL
    url = f"{GOVINFO_BASE_URL}/title-{title_num}/ECFR-title{title_num}.xml"
    
    # Attempt download with retries
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Downloading title {title_num} (attempt {attempt + 1})")
            
            # Create a session for connection pooling
            session = requests.Session()
            session.headers.update(HEADERS)
            
            response = session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save the XML file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(file_path)
            
            logger.info(f"Successfully downloaded title {title_num} ({file_size} bytes)")
            
            # Be nice to the server
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return True, file_path, file_size
            
        except Exception as e:
            logger.error(f"Error downloading title {title_num}: {str(e)}")
            
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to download title {title_num} after {MAX_RETRIES} attempts")
                return False, file_path, 0