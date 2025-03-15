#!/usr/bin/env python3

"""
Pipeline for downloading and processing eCFR data from the GovInfo Bulk Data Repository.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from .downloader import download_title, TITLE_NAMES
from .processor import extract_text_from_xml, generate_summary

# Setup logging
logger = logging.getLogger('bulk_pipeline')

def process_title(title_num: int, xml_dir: str, json_dir: str, force_download: bool = False) -> Optional[Dict[str, Any]]:
    """Download and process a title."""
    # Step 1: Download the XML
    success, xml_path, _ = download_title(title_num, xml_dir, not force_download)
    if not success:
        logger.error(f"Failed to download XML for title {title_num}")
        return None
    
    # Step 2: Process the XML
    title_data, json_path = extract_text_from_xml(xml_path, json_dir)
    return title_data

def process_all_titles(
    data_dir: str,
    max_workers: int = 3, 
    force_download: bool = False,
    title_nums: Optional[List[int]] = None
) -> Dict[int, Dict[str, Any]]:
    """Process all titles."""
    # Prepare directories
    xml_dir = os.path.join(data_dir, "xml")
    json_dir = os.path.join(data_dir, "processed")
    
    os.makedirs(xml_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    # Determine which titles to process
    titles_to_process = title_nums or list(TITLE_NAMES.keys())
    logger.info(f"Will process {len(titles_to_process)} titles with {max_workers} workers")
    
    # Process titles in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for title_num in titles_to_process:
            futures[executor.submit(
                process_title, 
                title_num=title_num,
                xml_dir=xml_dir,
                json_dir=json_dir,
                force_download=force_download
            )] = title_num
        
        # Wait for results
        results = {}
        success_count = 0
        
        for future in futures:
            title_num = futures[future]
            try:
                title_data = future.result()
                if title_data:
                    results[title_num] = title_data
                    success_count += 1
                    logger.info(f"Processed title {title_num} successfully")
                else:
                    logger.error(f"Failed to process title {title_num}")
            except Exception as e:
                logger.error(f"Exception processing title {title_num}: {e}")
    
    # Generate summary
    if results:
        generate_summary(results, json_dir)
    
    logger.info(f"Processed {success_count} of {len(titles_to_process)} titles successfully")
    
    return results

def display_title_info(title_num: int, data_dir: str):
    """Display information about a specific title."""
    json_dir = os.path.join(data_dir, "processed")
    json_path = os.path.join(json_dir, f"title-{title_num}.json")
    
    if not os.path.exists(json_path):
        print(f"No processed data found for title {title_num}")
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            title_data = json.load(f)
        
        print(f"\nTitle {title_num}: {title_data.get('name', '')}")
        print("=" * 80)
        print(f"Full name: {title_data.get('full_name', '')}")
        print(f"Agencies: {', '.join(title_data.get('agencies', []) or ['Unknown'])}")
        
        # Dates
        dates = title_data.get('dates', {})
        print(f"Latest amended: {dates.get('latest_amended_on') or 'unknown'}")
        print(f"Latest issue: {dates.get('latest_issue_date') or 'unknown'}")
        print(f"Up to date as of: {dates.get('up_to_date_as_of') or 'unknown'}")
        
        # Metrics
        metrics = title_data.get('metrics', {})
        print(f"Word count: {metrics.get('word_count', 0):,}")
        print(f"Section count: {metrics.get('section_count', 0):,}")
        print(f"Paragraph count: {metrics.get('paragraph_count', 0):,}")
        print(f"Chapter count: {metrics.get('chapter_count', 0):,}")
        
        # Structure
        chapters = title_data.get('chapters', [])
        if chapters:
            print(f"\nChapters ({len(chapters)}):")
            for i, chapter in enumerate(chapters[:5]):  # Show first 5 chapters
                print(f"  {chapter.get('number', '')}: {chapter.get('name', '')}")
            if len(chapters) > 5:
                print(f"  ... and {len(chapters) - 5} more")
        
        # Sections
        sections = title_data.get('sections', [])
        if sections:
            print(f"\nSections ({len(sections)}):")
            for i, section in enumerate(sections[:5]):  # Show first 5 sections
                print(f"  {section.get('number', '')}: {section.get('name', '')}")
                print(f"    Word count: {section.get('word_count', 0):,}")
            if len(sections) > 5:
                print(f"  ... and {len(sections) - 5} more")
        
    except Exception as e:
        print(f"Error reading title data: {e}")

def display_summary(data_dir: str):
    """Display summary information about all processed titles."""
    summary_path = os.path.join(data_dir, "processed", "summary.json")
    
    if not os.path.exists(summary_path):
        print("No summary data found. Process titles first.")
        return
    
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        print("\neCFR Processing Summary:")
        print("=" * 80)
        print(f"Processed {summary.get('total_titles', 0)} titles")
        
        # Total metrics
        metrics = summary.get('total_metrics', {})
        print(f"Total word count: {metrics.get('word_count', 0):,}")
        print(f"Total sections: {metrics.get('section_count', 0):,}")
        print(f"Total paragraphs: {metrics.get('paragraph_count', 0):,}")
        
        # Date range information
        date_ranges = summary.get('date_ranges', {})
        print("\nDate information:")
        print(f"  Latest amended: {date_ranges.get('latest_amended') or 'unknown'}")
        print(f"  Latest issue: {date_ranges.get('latest_issue') or 'unknown'}")
        
        # Top agencies
        agencies = summary.get('agencies', {})
        if agencies:
            print("\nTop agencies by number of titles:")
            agency_counts = sorted(agencies.items(), key=lambda x: x[1], reverse=True)
            for agency, count in agency_counts[:5]:
                print(f"  {agency}: {count} titles")
        
        # Title word counts
        titles = summary.get('titles', [])
        if titles:
            print("\nTitles by word count (top 10):")
            titles_by_words = sorted(titles, key=lambda x: x.get('metrics', {}).get('word_count', 0), reverse=True)
            for title in titles_by_words[:10]:
                word_count = title.get('metrics', {}).get('word_count', 0)
                print(f"  Title {title.get('number')}: {title.get('name')} - {word_count:,} words")
        
    except Exception as e:
        print(f"Error reading summary data: {e}")