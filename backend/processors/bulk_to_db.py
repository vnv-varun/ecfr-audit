#!/usr/bin/env python3

"""
eCFR Bulk Data to Database Pipeline
Downloads XML files from GovInfo bulk data repository, 
processes them, and loads the data into the database.
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import database modules
from backend.models.database import engine, Base, get_db
from backend.models.models import (
    Title, Agency, RegulationMetrics, Chapter, 
    Subchapter, Part, Subpart, Section, Paragraph
)

# Import the bulk processor modules
from backend.processors.bulk import (
    download_title, extract_text_from_xml, process_all_titles
)
from backend.processors.bulk.downloader import TITLE_NAMES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bulk_to_db')

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Convert ISO date string to datetime object."""
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def create_database_tables():
    """Create all database tables if they don't exist."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or already exist.")

def process_and_store_title(
    title_num: int, 
    xml_dir: str, 
    json_dir: str, 
    db_session: Session, 
    force_download: bool = False
) -> Optional[Dict[str, Any]]:
    """Download, process, and store a title in the database."""
    # Step 1: Download the XML
    success, xml_path, _ = download_title(title_num, xml_dir, not force_download)
    if not success:
        logger.error(f"Failed to download XML for title {title_num}")
        return None
    
    # Step 2: Process the XML
    title_data, json_path = extract_text_from_xml(xml_path, json_dir)
    if not title_data:
        logger.error(f"Failed to process XML for title {title_num}")
        return None
    
    # Step 3: Store in database
    try:
        # Check if title already exists
        existing_title = db_session.query(Title).filter(Title.number == title_num).first()
        
        if existing_title:
            logger.info(f"Updating existing title {title_num}")
            
            # Update basic title information
            existing_title.name = title_data.get("name", "")
            existing_title.full_name = title_data.get("full_name", "")
            existing_title.reserved = False
            
            # Update dates
            dates = title_data.get("dates", {})
            existing_title.up_to_date_as_of = parse_date(dates.get("up_to_date_as_of"))
            existing_title.latest_amended_on = parse_date(dates.get("latest_amended_on"))
            existing_title.latest_issue_date = parse_date(dates.get("latest_issue_date"))
            
            title_obj = existing_title
            db_session.commit()
        else:
            # Create new title
            title_obj = Title(
                number=title_num,
                name=title_data.get("name", ""),
                full_name=title_data.get("full_name", ""),
                reserved=False,
                source_url=title_data.get("source_url")
            )
            
            # Set dates
            dates = title_data.get("dates", {})
            title_obj.up_to_date_as_of = parse_date(dates.get("up_to_date_as_of"))
            title_obj.latest_amended_on = parse_date(dates.get("latest_amended_on"))
            title_obj.latest_issue_date = parse_date(dates.get("latest_issue_date"))
            
            db_session.add(title_obj)
            db_session.commit()
            db_session.refresh(title_obj)
        
        # Process agencies
        agencies = title_data.get("agencies", [])
        process_agencies(db_session, title_obj, agencies)
        
        # Process metrics
        metrics = title_data.get("metrics", {})
        process_metrics(db_session, title_obj, metrics)
        
        # Process chapters and sections if they exist
        process_chapters(db_session, title_obj, title_data.get("chapters", []))
        process_sections(db_session, title_obj, title_data.get("sections", []))
        
        return title_data
        
    except Exception as e:
        logger.error(f"Error storing title {title_num} in database: {e}")
        db_session.rollback()
        return None

def process_agencies(db_session: Session, title_obj: Title, agencies: List[str]):
    """Process and store agencies in the database."""
    # Clear existing agencies first
    for agency_name in agencies:
        if not agency_name:
            continue
            
        # Check if agency exists
        existing_agency = db_session.query(Agency).filter(
            Agency.name == agency_name
        ).first()
        
        if existing_agency:
            # Associate with title if not already
            if existing_agency not in title_obj.agencies:
                title_obj.agencies.append(existing_agency)
        else:
            # Create new agency
            agency = Agency(
                name=agency_name,
                identifier=f"agency-{agency_name.lower().replace(' ', '-')}"
            )
            db_session.add(agency)
            title_obj.agencies.append(agency)
    
    db_session.commit()

def process_metrics(db_session: Session, title_obj: Title, metrics: Dict[str, int]):
    """Process and store metrics in the database."""
    # Just create new metrics - don't try to query existing ones
    metrics_obj = RegulationMetrics(
        title_id=title_obj.id,
        word_count=metrics.get("word_count", 0),
        section_count=metrics.get("section_count", 0),
        paragraph_count=metrics.get("paragraph_count", 0)
    )
    db_session.add(metrics_obj)
    db_session.commit()

def process_chapters(db_session: Session, title_obj: Title, chapters: List[Dict[str, Any]]):
    """Process and store chapters in the database."""
    # First clear existing chapters
    for chapter in chapters:
        chapter_num = chapter.get("number", "")
        if not chapter_num:
            continue
            
        # Check if chapter exists
        existing_chapter = db_session.query(Chapter).filter(
            Chapter.number == chapter_num,
            Chapter.title_id == title_obj.id
        ).first()
        
        if existing_chapter:
            # Update chapter
            existing_chapter.name = chapter.get("name", "")
            existing_chapter.identifier = chapter.get("identifier", "")
            existing_chapter.description = chapter.get("description", "")
            existing_chapter.agency_name = chapter.get("agency_name", "")
        else:
            # Create new chapter
            chapter_obj = Chapter(
                number=chapter_num,
                name=chapter.get("name", ""),
                title_id=title_obj.id,
                identifier=chapter.get("identifier", ""),
                description=chapter.get("description", ""),
                agency_name=chapter.get("agency_name", "")
            )
            db_session.add(chapter_obj)
    
    db_session.commit()

def process_sections(db_session: Session, title_obj: Title, sections: List[Dict[str, Any]]):
    """Process and store sections in the database."""
    # Store sections - these might be root sections not associated with parts
    for section in sections:
        section_num = section.get("number", "")
        if not section_num:
            continue
            
        # Check if section exists
        existing_section = db_session.query(Section).filter(
            Section.number == section_num,
            Section.part_id == None  # Only get root sections
        ).first()
        
        if existing_section:
            # Update section
            existing_section.name = section.get("name", "")
            existing_section.text_content = section.get("content", "")
            existing_section.full_identifier = section.get("full_identifier", "")
        else:
            # Create new section
            section_obj = Section(
                number=section_num,
                name=section.get("name", ""),
                text_content=section.get("content", ""),
                full_identifier=section.get("full_identifier", "")
            )
            db_session.add(section_obj)
            
            # Process paragraphs
            for i, para in enumerate(section.get("paragraphs", [])):
                para_obj = Paragraph(
                    identifier=para.get("identifier", f"p{i}"),
                    text_content=para.get("content", ""),
                    level=para.get("level", 1),
                    order_index=i
                )
                section_obj.paragraphs.append(para_obj)
    
    db_session.commit()

def process_all_titles_to_db(
    data_dir: str,
    max_workers: int = 3, 
    force_download: bool = False,
    title_nums: Optional[List[int]] = None
) -> int:
    """Process all titles and store in the database."""
    # Prepare directories
    xml_dir = os.path.join(data_dir, "xml")
    json_dir = os.path.join(data_dir, "processed")
    
    os.makedirs(xml_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Create database tables
    create_database_tables()
    
    # Determine which titles to process
    titles_to_process = title_nums or list(TITLE_NAMES.keys())
    logger.info(f"Will process {len(titles_to_process)} titles with {max_workers} workers")
    
    # Process titles sequentially (database operations)
    success_count = 0
    db = next(get_db())
    
    try:
        for title_num in titles_to_process:
            title_data = process_and_store_title(
                title_num=title_num,
                xml_dir=xml_dir,
                json_dir=json_dir,
                db_session=db,
                force_download=force_download
            )
            
            if title_data:
                success_count += 1
                logger.info(f"Processed and stored title {title_num} successfully")
            else:
                logger.error(f"Failed to process or store title {title_num}")
    
    finally:
        db.close()
    
    logger.info(f"Processed {success_count} of {len(titles_to_process)} titles successfully")
    
    return success_count

def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="Download, process, and store eCFR data in the database")
    parser.add_argument("--data-dir", default="./data", help="Base directory for data storage")
    parser.add_argument("--max-workers", type=int, default=2, help="Maximum number of parallel workers")
    parser.add_argument("--title", type=int, help="Process a specific title only")
    parser.add_argument("--titles", type=str, help="Comma-separated list of titles to process")
    parser.add_argument("--force", action="store_true", help="Force download even if files exist")
    parser.add_argument("--download-only", action="store_true", help="Only download XML files without processing")
    parser.add_argument("--info", action="store_true", help="Print database information and exit")
    
    args = parser.parse_args()
    
    # Define directories
    data_dir = args.data_dir
    xml_dir = os.path.join(data_dir, "xml")
    json_dir = os.path.join(data_dir, "processed")
    
    # Create directories
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(xml_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Database info mode
    if args.info:
        db = next(get_db())
        try:
            title_count = db.query(Title).count()
            agency_count = db.query(Agency).count()
            section_count = db.query(Section).count()
            
            print("\neCFR Database Information:")
            print("=" * 80)
            print(f"Titles: {title_count}")
            print(f"Agencies: {agency_count}")
            print(f"Sections: {section_count}")
            
            # Print title metrics
            metrics = db.query(
                Title.number, 
                Title.name, 
                RegulationMetrics.word_count
            ).join(
                RegulationMetrics, 
                RegulationMetrics.title_id == Title.id
            ).all()
            
            if metrics:
                print("\nTitle Metrics:")
                for title_num, title_name, word_count in sorted(metrics, key=lambda x: x[0]):
                    print(f"  Title {title_num}: {title_name} - {word_count or 0:,} words")
            
            return 0
        finally:
            db.close()
    
    # Determine titles to process
    title_nums = None
    if args.title:
        title_nums = [args.title]
    elif args.titles:
        try:
            title_nums = [int(t.strip()) for t in args.titles.split(',')]
        except ValueError:
            logger.error("Invalid title format. Please use comma-separated integers.")
            return 1
    
    # Download only
    if args.download_only:
        if title_nums:
            for title_num in title_nums:
                success, file_path, file_size = download_title(title_num, xml_dir, not args.force)
                print(f"Title {title_num}: {'Success' if success else 'Failed'} ({file_size} bytes)")
        else:
            # Download all titles
            for title_num in TITLE_NAMES.keys():
                success, file_path, file_size = download_title(title_num, xml_dir, not args.force)
                print(f"Title {title_num}: {'Success' if success else 'Failed'} ({file_size} bytes)")
        return 0
    
    # Process titles and store in database
    success_count = process_all_titles_to_db(
        data_dir=data_dir,
        max_workers=args.max_workers,
        force_download=args.force,
        title_nums=title_nums
    )
    
    if success_count > 0:
        print("\nProcess completed successfully!")
        print(f"Processed and stored {success_count} titles in the database.")
        return 0
    else:
        print("\nProcess failed: No titles were successfully processed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())