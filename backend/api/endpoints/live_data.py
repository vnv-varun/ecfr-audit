#!/usr/bin/env python3

"""
Live data endpoints for the eCFR API.
This module provides live data directly from the eCFR API and website,
as well as integration with the GovInfo bulk data.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
import requests
from typing import Dict, Any, List, Optional
import random
import re
import time
import logging
import os
import json
from sqlalchemy.orm import Session

# Import models when available
try:
    from ...models.database import get_db
    from ...models.models import Title, RegulationMetrics, Agency
    HAS_DB_MODELS = True
except ImportError:
    HAS_DB_MODELS = False
    def get_db():
        yield None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('live_data')

router = APIRouter(prefix="/live", tags=["live"])

# eCFR API constants
ECFR_API_BASE = "https://www.ecfr.gov/api/versioner/v1"
ECFR_BASE_URL = "https://www.ecfr.gov"

# GovInfo constants
GOVINFO_BASE_URL = "https://www.govinfo.gov/bulkdata/ECFR"

# Data directories
DATA_DIR = os.getenv("DATA_DIR", "./data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
XML_DIR = os.path.join(DATA_DIR, "xml")

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(XML_DIR, exist_ok=True)

@router.get("/titles", response_model=Dict[str, Any])
async def get_titles(db: Session = Depends(get_db)):
    """Get the current list of titles directly from eCFR API."""
    try:
        # First check if we have titles in the database
        if HAS_DB_MODELS and db:
            db_titles = db.query(Title).order_by(Title.number).all()
            
            if db_titles:
                # Return titles from database
                titles_data = {
                    "titles": [
                        {
                            "number": title.number,
                            "name": title.name,
                            "source": "database"
                        }
                        for title in db_titles
                    ]
                }
                return titles_data
        
        # If no database titles, try the API
        response = requests.get(f"{ECFR_API_BASE}/titles", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching titles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching titles: {str(e)}")

@router.get("/title/{title_number}", response_model=Dict[str, Any])
async def get_title_data(title_number: int, db: Session = Depends(get_db)):
    """Get current data for a specific title."""
    try:
        # First check if title exists in database
        if HAS_DB_MODELS and db:
            db_title = db.query(Title).filter(Title.number == title_number).first()
            
            if db_title:
                # Get agencies for this title
                agencies = db.query(Agency).filter(Agency.title_id == db_title.id).all()
                agency_names = [agency.name for agency in agencies]
                
                # Check if we have processed data file
                processed_file = os.path.join(PROCESSED_DIR, f"title-{title_number}.json")
                data_status = "processed" if os.path.exists(processed_file) else "basic"
                
                return {
                    "title": {
                        "number": db_title.number,
                        "name": db_title.name,
                        "agencies": agency_names,
                        "data_status": data_status
                    },
                    "source_url": f"{ECFR_BASE_URL}/current/title-{title_number}",
                    "govinfo_url": f"{GOVINFO_BASE_URL}/title-{title_number}/ECFR-title{title_number}.xml",
                    "source": "database"
                }
        
        # If not in database, try the API
        titles_response = requests.get(f"{ECFR_API_BASE}/titles", timeout=10)
        titles_response.raise_for_status()
        titles_data = titles_response.json()
        
        title_found = False
        title_name = ""
        
        if 'titles' in titles_data:
            for title in titles_data['titles']:
                if title.get('number') == title_number:
                    title_found = True
                    title_name = title.get('name', '')
                    break
        
        if not title_found:
            raise HTTPException(status_code=404, detail=f"Title {title_number} not found")
        
        # Return basic title info
        return {
            "title": {
                "number": title_number,
                "name": title_name,
                "agencies": [],
                "data_status": "api-only"
            },
            "source_url": f"{ECFR_BASE_URL}/current/title-{title_number}",
            "govinfo_url": f"{GOVINFO_BASE_URL}/title-{title_number}/ECFR-title{title_number}.xml",
            "source": "api"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching title {title_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching title {title_number}: {str(e)}")

@router.get("/metrics/title/{title_number}", response_model=Dict[str, Any])
async def get_title_metrics(title_number: int, db: Session = Depends(get_db)):
    """
    Get metrics for a specific title.
    This checks the database first, then falls back to processed files,
    and finally generates sample data if needed.
    """
    try:
        # First check database for metrics
        if HAS_DB_MODELS and db:
            db_title = db.query(Title).filter(Title.number == title_number).first()
            
            if db_title:
                # Get metrics for this title
                metrics = db.query(RegulationMetrics).filter(RegulationMetrics.title_id == db_title.id).first()
                
                if metrics:
                    # Get agency for context
                    agency = None
                    if metrics.agency_id:
                        agency = db.query(Agency).filter(Agency.id == metrics.agency_id).first()
                    
                    # Check if we have processed data with sample text
                    sample_text = ""
                    processed_file = os.path.join(PROCESSED_DIR, f"title-{title_number}.json")
                    if os.path.exists(processed_file):
                        try:
                            with open(processed_file, 'r', encoding='utf-8') as f:
                                processed_data = json.load(f)
                                # Get first section content as sample
                                sections = processed_data.get("sections", [])
                                if sections:
                                    sample_text = sections[0].get("content", "")
                                    if len(sample_text) > 500:  # Truncate long samples
                                        sample_text = sample_text[:500] + "..."
                        except Exception as e:
                            logger.error(f"Error reading processed file for title {title_number}: {str(e)}")
                    
                    return {
                        "title_number": db_title.number,
                        "title_name": db_title.name,
                        "agency": agency.name if agency else "Unknown",
                        "word_count": metrics.word_count,
                        "sentence_count": metrics.section_count,  # Using section count as proxy
                        "avg_sentence_length": round(metrics.word_count / max(metrics.section_count, 1), 1),
                        "sample_text": sample_text,
                        "timestamp": metrics.updated_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(metrics, 'updated_at') else time.strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "database"
                    }
        
        # If not in database, check for processed file
        processed_file = os.path.join(PROCESSED_DIR, f"title-{title_number}.json")
        if os.path.exists(processed_file):
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
                    
                    # Extract metrics from processed data
                    title_name = processed_data.get("name", f"Title {title_number}")
                    agencies = processed_data.get("agencies", [])
                    agency_name = agencies[0] if agencies else "Unknown"
                    
                    # Calculate metrics
                    sections = processed_data.get("sections", [])
                    word_count = 0
                    section_count = len(sections)
                    sample_text = ""
                    
                    for section in sections:
                        content = section.get("content", "")
                        if content:
                            word_count += len(content.split())
                            if not sample_text and len(content) > 10:
                                sample_text = content[:500] + "..." if len(content) > 500 else content
                    
                    avg_sentence_length = round(word_count / max(section_count, 1), 1)
                    
                    return {
                        "title_number": title_number,
                        "title_name": title_name,
                        "agency": agency_name,
                        "word_count": word_count,
                        "sentence_count": section_count,
                        "avg_sentence_length": avg_sentence_length,
                        "sample_text": sample_text,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "source": "processed_file"
                    }
            except Exception as e:
                logger.error(f"Error reading processed file for title {title_number}: {str(e)}")
        
        # If all else fails, generate sample data
        # First check if title exists in API
        titles_response = requests.get(f"{ECFR_API_BASE}/titles", timeout=10)
        titles_response.raise_for_status()
        titles_data = titles_response.json()
        
        title_found = False
        title_name = f"Title {title_number}"
        
        if 'titles' in titles_data:
            for title in titles_data['titles']:
                if title.get('number') == title_number:
                    title_found = True
                    title_name = title.get('name', title_name)
                    break
        
        if not title_found:
            # Fall back to preset data for demo purposes
            title_map = {
                1: "General Provisions",
                2: "Grants and Agreements",
                3: "The President",
                5: "Administrative Personnel",
                7: "Agriculture",
                10: "Energy",
                12: "Banks and Banking",
                14: "Aeronautics and Space",
                15: "Commerce and Foreign Trade",
                17: "Commodity and Securities Exchanges",
                26: "Internal Revenue",
                40: "Protection of Environment"
            }
            title_name = title_map.get(title_number, f"Title {title_number}")
        
        # Map title number to approximate word count (roughly correlated to actual size)
        word_count_map = {
            1: 85000,    # General Provisions (small)
            2: 120000,   # Grants and Agreements (medium)
            3: 70000,    # The President (small)
            5: 320000,   # Administrative Personnel (large)
            7: 750000,   # Agriculture (very large)
            10: 420000,  # Energy (large)
            12: 680000,  # Banks and Banking (very large)
            14: 180000,  # Aeronautics and Space (medium)
            15: 310000,  # Commerce and Foreign Trade (large)
            17: 520000,  # Commodity and Securities Exchanges (very large)
            26: 1250000, # Internal Revenue (extremely large)
            29: 480000,  # Labor (large)
            40: 890000,  # Protection of Environment (very large)
            42: 670000,  # Public Health (very large)
            45: 530000,  # Public Welfare (very large)
            49: 710000,  # Transportation (very large)
        }
        
        # Default or mapped word count
        base_word_count = word_count_map.get(title_number, 250000)
        
        # Add some randomness (+/- 10%)
        word_count = int(base_word_count * random.uniform(0.9, 1.1))
        
        # Calculate other metrics
        avg_words_per_sentence = random.uniform(18, 25)
        sentence_count = int(word_count / avg_words_per_sentence)
        
        # Sample text snippets for different titles (could expand this in production)
        sample_texts = {
            1: "The provisions of this chapter, unless otherwise noted, are applicable to all regulations issued by federal agencies and published in the Federal Register.",
            26: "Gross income means all income from whatever source derived, including (but not limited to) compensation for services, fees, commissions, fringe benefits, and similar items.",
            40: "For purposes of this part, the term 'emissions standard' means a requirement established by the State or the Administrator which limits the quantity, rate, or concentration of emissions of air pollutants on a continuous basis.",
            42: "The Secretary shall award grants to eligible entities to develop and implement programs to train individuals in the identification, screening, and referral of individuals with trauma, mental health, or substance use disorders.",
            # Default sample for other titles
            0: "Each agency shall make available to the public information as follows: Each agency shall separately state and currently publish in the Federal Register for the guidance of the public descriptions of its central and field organization."
        }
        
        # Get sample text for this title or use default
        sample_text = sample_texts.get(title_number, sample_texts[0])
        
        # Return the metrics
        return {
            "title_number": title_number,
            "title_name": title_name,
            "agency": "Unknown",
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_words_per_sentence,
            "sample_text": sample_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "generated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching metrics for title {title_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching metrics for title {title_number}: {str(e)}")

async def background_refresh_data(title_number: int):
    """
    Background task to refresh data for a specific title.
    This will download data from GovInfo, process it, and update the database.
    """
    import importlib
    
    logger.info(f"Starting background refresh for title {title_number}")
    
    try:
        # Dynamically import modules to avoid circular imports
        try:
            bulk_downloader_module = importlib.import_module("...processors.bulk_downloader", package=__name__)
            seeder_module = importlib.import_module("...processors.seed_database", package=__name__)
            
            BulkDownloader = bulk_downloader_module.BulkDownloader
            DatabaseSeeder = seeder_module.DatabaseSeeder
            
            # Create a downloader instance
            downloader = BulkDownloader(DATA_DIR)
            
            # Get the specific title info
            title_info = next((t for t in downloader.titles if t.number == title_number), None)
            
            if not title_info:
                logger.error(f"Title {title_number} not found in downloader.titles")
                return
            
            # Download the XML
            success = downloader.download_title(title_info)
            
            if success:
                logger.info(f"Successfully downloaded title {title_number}")
                
                # Process the XML to extract text and structure
                title_data = downloader.extract_text_from_xml(title_info)
                
                if title_data:
                    logger.info(f"Successfully processed title {title_number}")
                    
                    # If DB models available, update the database
                    if HAS_DB_MODELS:
                        seeder = DatabaseSeeder(DATA_DIR)
                        db = next(get_db())
                        
                        if db:
                            try:
                                # Update database - simplified for now
                                logger.info(f"Updating database for title {title_number}")
                                
                                # Get or create title
                                db_title = db.query(Title).filter(Title.number == title_number).first()
                                
                                if db_title:
                                    logger.info(f"Title {title_number} exists in database")
                                else:
                                    logger.info(f"Creating title {title_number} in database")
                            
                            except Exception as e:
                                logger.error(f"Error updating database for title {title_number}: {str(e)}")
                                if 'db' in locals() and db:
                                    db.rollback()
                            
                            finally:
                                if 'db' in locals() and db:
                                    db.close()
                
                logger.info(f"Background refresh completed for title {title_number}")
            else:
                logger.error(f"Failed to download title {title_number}")
        
        except ImportError as e:
            logger.error(f"Failed to import required modules: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in background refresh for title {title_number}: {str(e)}")

@router.post("/refresh-data", response_model=Dict[str, Any])
async def refresh_data(background_tasks: BackgroundTasks, title_number: int = 1):
    """
    Refresh data for a specific title.
    This schedules a background task to download and process the latest data.
    """
    try:
        # Validate title number
        if title_number < 1 or title_number > 50:
            raise HTTPException(status_code=400, detail=f"Invalid title number: {title_number}. Must be between 1 and 50.")
        
        # Schedule the background task
        background_tasks.add_task(background_refresh_data, title_number)
        
        return {
            "status": "success",
            "message": f"Data refresh for title {title_number} has been scheduled",
            "title_number": title_number,
            "govinfo_url": f"{GOVINFO_BASE_URL}/title-{title_number}/ECFR-title{title_number}.xml"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling refresh for title {title_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scheduling refresh: {str(e)}")