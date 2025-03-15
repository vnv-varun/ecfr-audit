#!/usr/bin/env python3

"""
Processor for GovInfo Bulk XML eCFR data.
Extracts structured content from XML files.
"""

import os
import re
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Setup logging
logger = logging.getLogger('bulk_processor')

from .downloader import TITLE_NAMES

def extract_date(text):
    """
    Extract a date from text in various formats.
    Returns ISO format date string (YYYY-MM-DD) or None if no date found.
    """
    if not text:
        return None
    
    # Common date patterns
    patterns = [
        # ISO format: 2023-01-31
        r'(\d{4}-\d{1,2}-\d{1,2})',
        # US format with full month name: January 31, 2023
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
        # US format with abbreviated month: Jan. 31, 2023
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\.]*\s+(\d{1,2}),?\s+(\d{4})',
        # US format with slash or dash: 01/31/2023, 01-31-2023
        r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, text)
        if matches:
            groups = matches.groups()
            
            if len(groups) == 1:
                # Already in ISO format
                return groups[0]
            elif len(groups) == 3:
                if groups[0] in ['January', 'February', 'March', 'April', 'May', 'June', 
                                'July', 'August', 'September', 'October', 'November', 'December']:
                    # Convert full month name to number
                    month_names = {
                        'January': '01', 'February': '02', 'March': '03', 'April': '04',
                        'May': '05', 'June': '06', 'July': '07', 'August': '08',
                        'September': '09', 'October': '10', 'November': '11', 'December': '12'
                    }
                    month = month_names[groups[0]]
                    day = groups[1].zfill(2)
                    year = groups[2]
                    return f"{year}-{month}-{day}"
                elif groups[0] in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                    # Convert abbreviated month to number
                    month_abbr = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    month = month_abbr[groups[0]]
                    day = groups[1].zfill(2)
                    year = groups[2]
                    return f"{year}-{month}-{day}"
                else:
                    # MM/DD/YYYY or MM-DD-YYYY format
                    month = groups[0].zfill(2)
                    day = groups[1].zfill(2)
                    year = groups[2]
                    return f"{year}-{month}-{day}"
    
    return None

def extract_text_from_xml(xml_file_path, output_dir):
    """
    Extract key information from the XML file for a title.
    Returns a comprehensive dictionary with the full hierarchy and content.
    """
    if not os.path.exists(xml_file_path):
        logger.error(f"File not found: {xml_file_path}")
        return None, None
    
    # Get title number from filename
    title_num = None
    file_name = os.path.basename(xml_file_path)
    match = re.match(r'title-(\d+)\.xml', file_name)
    if match:
        title_num = int(match.group(1))
    else:
        logger.error(f"Could not extract title number from filename: {file_name}")
        return None, None
    
    try:
        logger.info(f"Processing XML for title {title_num}")
        
        # Parse the XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Extract content with full hierarchy
        title_data = {
            "number": title_num,
            "name": TITLE_NAMES.get(title_num, ""),
            "full_name": f"Title {title_num}: {TITLE_NAMES.get(title_num, '')}",
            "agencies": [],
            "chapters": [],
            "parts": [],
            "sections": [],
            "metadata": {},
            "dates": {
                "latest_amended_on": None,
                "latest_issue_date": None,
                "up_to_date_as_of": None,
                "processed_date": datetime.now().strftime("%Y-%m-%d")
            },
            "source_file": xml_file_path,
            "source_url": f"https://www.ecfr.gov/current/title-{title_num}",
            "govinfo_url": f"https://www.govinfo.gov/bulkdata/ECFR/title-{title_num}/ECFR-title{title_num}.xml"
        }
        
        # Find all text tags using namespaces if needed
        ns = {'': root.tag.split('}')[0].strip('{') if '}' in root.tag else ''}
        
        # Try to extract title name
        title_elem = root.find(".//DIV1/HEAD", ns) or root.find(".//TITLE", ns)
        if title_elem is not None and title_elem.text:
            title_name = title_elem.text.strip()
            title_data["name"] = title_name
            title_data["full_name"] = f"Title {title_num}: {title_name}"
        elif title_elem is not None:
            title_attr = title_elem.get("TITLE-NAME")
            if title_attr:
                title_data["name"] = title_attr
                title_data["full_name"] = f"Title {title_num}: {title_attr}"
        
        # Extract date information from AMDDATE
        amd_date_elem = root.find(".//AMDDATE", ns)
        if amd_date_elem is not None and amd_date_elem.text:
            date_text = amd_date_elem.text.strip()
            extracted_date = extract_date(date_text)
            if extracted_date:
                title_data["dates"]["latest_amended_on"] = extracted_date
                
        # Extract sections directly from DIV8 elements
        section_count = 0
        total_word_count = 0
        total_paragraph_count = 0
        
        for section in root.findall(".//DIV8[@TYPE='SECTION']", ns):
            section_num = section.get("N", "")
            section_title = ""
            
            # Get section title from HEAD tag
            head_elem = section.find("./HEAD", ns)
            if head_elem is not None and head_elem.text:
                section_title = head_elem.text.strip()
            
            # Extract paragraphs
            paragraphs = []
            para_index = 0
            
            for p in section.findall("./P", ns):
                para_text = "".join(p.itertext()).strip()
                if para_text:
                    para_id = f"p{para_index}"
                    para_index += 1
                    
                    paragraphs.append({
                        "identifier": para_id,
                        "content": para_text,
                        "level": 1
                    })
            
            # Get the raw text content
            content = "".join(section.itertext()).strip()
            
            # Calculate metrics
            if content:
                word_count = len(content.split())
                total_word_count += word_count
            else:
                word_count = 0
            
            total_paragraph_count += len(paragraphs)
            
            # Create section info
            section_info = {
                "number": section_num,
                "name": section_title,
                "full_identifier": section_num,
                "content": content,
                "word_count": word_count,
                "paragraphs": paragraphs
            }
            
            # Add to title data
            title_data["sections"].append(section_info)
            section_count += 1
        
        # Extract chapters (DIV5 elements)
        for chapter in root.findall(".//DIV5", ns):
            chapter_num = chapter.get("N", "")
            chapter_name = ""
            
            # Get chapter title
            head_elem = chapter.find("./HEAD", ns)
            if head_elem is not None and head_elem.text:
                chapter_name = head_elem.text.strip()
            
            # Create chapter info
            chapter_info = {
                "number": chapter_num,
                "name": chapter_name,
                "identifier": chapter_num,
                "parts": []
            }
            
            # Extract agency info
            agency_elem = chapter.find(".//AGENCY", ns)
            if agency_elem is not None:
                agency_name = agency_elem.get("AGENCY-NAME", "")
                if agency_name and agency_name not in title_data["agencies"]:
                    title_data["agencies"].append(agency_name)
            
            # Add to title data
            title_data["chapters"].append(chapter_info)
        
        # Calculate metrics
        title_data["metrics"] = {
            "word_count": total_word_count,
            "section_count": section_count,
            "paragraph_count": total_paragraph_count,
            "chapter_count": len(title_data["chapters"]),
            "part_count": len(title_data["parts"])
        }
        
        # Save the processed data
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"title-{title_num}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(title_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully processed title {title_num} - {title_data['name']}")
        logger.info(f"  Words: {total_word_count}, Sections: {section_count}, Paragraphs: {total_paragraph_count}")
        logger.info(f"  Date info: Updated as of {title_data['dates']['latest_amended_on'] or 'unknown'}")
        
        return title_data, output_file
        
    except Exception as e:
        logger.error(f"Error processing XML for title {title_num}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def generate_summary(results: Dict[int, Dict[str, Any]], output_dir: str):
    """Generate summary data for all processed titles."""
    if not results:
        logger.error("No results to generate summary from")
        return
    
    summary = {
        "total_titles": len(results),
        "titles": [],
        "agencies": defaultdict(int),
        "date_ranges": {
            "earliest_amended": None,
            "latest_amended": None,
            "earliest_issue": None,
            "latest_issue": None,
            "earliest_update": None,
            "latest_update": None,
            "processing_date": datetime.now().strftime("%Y-%m-%d")
        },
        "total_metrics": {
            "word_count": 0,
            "section_count": 0,
            "paragraph_count": 0,
            "part_count": 0,
            "chapter_count": 0
        }
    }
    
    # Collect data from all titles
    for title_num, title_data in results.items():
        title_summary = {
            "number": title_num,
            "name": title_data.get("name", ""),
            "agencies": title_data.get("agencies", []),
            "dates": title_data.get("dates", {}),
            "metrics": title_data.get("metrics", {})
        }
        
        summary["titles"].append(title_summary)
        
        # Add to agency counts
        for agency in title_data.get("agencies", []):
            summary["agencies"][agency] += 1
        
        # Add to total metrics
        metrics = title_data.get("metrics", {})
        for key, value in metrics.items():
            if key in summary["total_metrics"]:
                summary["total_metrics"][key] += value
        
        # Update date ranges
        dates = title_data.get("dates", {})
        
        # Amended dates
        amended_date = dates.get("latest_amended_on")
        if amended_date:
            if not summary["date_ranges"]["earliest_amended"] or amended_date < summary["date_ranges"]["earliest_amended"]:
                summary["date_ranges"]["earliest_amended"] = amended_date
            if not summary["date_ranges"]["latest_amended"] or amended_date > summary["date_ranges"]["latest_amended"]:
                summary["date_ranges"]["latest_amended"] = amended_date
        
        # Issue dates
        issue_date = dates.get("latest_issue_date")
        if issue_date:
            if not summary["date_ranges"]["earliest_issue"] or issue_date < summary["date_ranges"]["earliest_issue"]:
                summary["date_ranges"]["earliest_issue"] = issue_date
            if not summary["date_ranges"]["latest_issue"] or issue_date > summary["date_ranges"]["latest_issue"]:
                summary["date_ranges"]["latest_issue"] = issue_date
        
        # Update dates
        update_date = dates.get("up_to_date_as_of")
        if update_date:
            if not summary["date_ranges"]["earliest_update"] or update_date < summary["date_ranges"]["earliest_update"]:
                summary["date_ranges"]["earliest_update"] = update_date
            if not summary["date_ranges"]["latest_update"] or update_date > summary["date_ranges"]["latest_update"]:
                summary["date_ranges"]["latest_update"] = update_date
    
    # Sort titles by number
    summary["titles"].sort(key=lambda x: x["number"])
    
    # Convert agencies from defaultdict to regular dict
    summary["agencies"] = dict(summary["agencies"])
    
    # Save summary to file
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Generated summary for {len(results)} titles")
    logger.info(f"Total word count: {summary['total_metrics']['word_count']:,}")
    logger.info(f"Date range: {summary['date_ranges'].get('earliest_amended')} to {summary['date_ranges'].get('latest_amended')}")
    
    return summary