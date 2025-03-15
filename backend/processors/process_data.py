#!/usr/bin/env python3

"""
Data processing script for eCFR Analyzer.

This script:
1. Fetches data from the eCFR API or uses cached data
2. Processes the regulation text
3. Calculates metrics
4. Stores results in the database
"""

import os
import sys
import logging
import json
import argparse
from typing import List, Dict, Any, Optional
import concurrent.futures
from pathlib import Path
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('process_data')

# To be replaced with actual imports
# from ..models.database import engine, get_db, Base
# from ..models.models import Agency, Title, Regulation, RegulationMetrics, Term, TermFrequency
# from ..utils.config import settings
# from .analyzer import analyze_text, count_words, calculate_readability, extract_term_frequencies

def setup_database():
    """Create database tables if they don't exist."""
    logger.info("Setting up database...")
    # Base.metadata.create_all(bind=engine)
    logger.info("Database setup complete.")

def load_cached_regulations(data_dir: str) -> List[Dict[str, Any]]:
    """Load regulations from cached files."""
    logger.info(f"Loading cached regulations from {data_dir}")
    
    regulations = []
    formatted_dir = os.path.join(data_dir, "formatted")
    
    if not os.path.exists(formatted_dir):
        logger.warning(f"Formatted directory not found at {formatted_dir}")
        return regulations
    
    # Walk through the formatted directory
    for root, dirs, files in os.walk(formatted_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    # Extract hierarchy from path
                    rel_path = os.path.relpath(file_path, formatted_dir)
                    parts = Path(rel_path).parts
                    
                    # Extract agency and title if available in path
                    agency = parts[0] if len(parts) > 0 else "Unknown"
                    title = parts[1] if len(parts) > 1 else "Unknown"
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic parsing of markdown content
                    lines = content.split('\n')
                    name = lines[0].replace('# ', '') if lines and lines[0].startswith('# ') else file
                    
                    # Extract URL and identifier if present
                    url = ""
                    identifier = ""
                    for line in lines:
                        if line.startswith('Source:'):
                            url = line.replace('Source:', '').strip()
                        elif line.startswith('Identifier:'):
                            identifier = line.replace('Identifier:', '').strip()
                    
                    # Create regulation object
                    regulation = {
                        'identifier': identifier or os.path.splitext(file)[0],
                        'name': name,
                        'agency': agency.replace('Agency_', '').replace('_', ' '),
                        'title': title.replace('Title_', '').replace('_', ' '),
                        'html_url': url,
                        'text_content': content,
                        'path': file_path
                    }
                    
                    regulations.append(regulation)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
    
    logger.info(f"Loaded {len(regulations)} regulations from cache")
    return regulations

def process_regulations(regulations: List[Dict[str, Any]], max_workers: int = 4) -> Dict[str, Any]:
    """Process regulations and extract metrics."""
    logger.info(f"Processing {len(regulations)} regulations with {max_workers} workers")
    
    # Placeholder for now - would use the actual analyzer in production
    def process_regulation(reg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'regulation_id': reg['identifier'],
            'title': reg['name'],
            'agency': reg['agency'],
            'word_count': len(reg['text_content'].split()),
            'readability_score': 50.0,  # Placeholder
            'sentence_count': reg['text_content'].count('.'),
            'paragraph_count': reg['text_content'].count('\n\n')
        }
    
    results = []
    
    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_reg = {executor.submit(process_regulation, reg): reg for reg in regulations}
        for future in concurrent.futures.as_completed(future_to_reg):
            reg = future_to_reg[future]
            try:
                result = future.result()
                results.append(result)
                logger.debug(f"Processed regulation {reg['identifier']}")
            except Exception as e:
                logger.error(f"Error processing regulation {reg['identifier']}: {e}")
    
    # Convert to DataFrame for aggregation
    df = pd.DataFrame(results)
    
    # Calculate aggregate metrics
    metrics = {
        'total_regulations': len(df),
        'total_word_count': int(df['word_count'].sum()),
        'average_readability': float(df['readability_score'].mean()),
        'average_word_count': int(df['word_count'].mean()),
        'by_agency': df.groupby('agency').agg({
            'word_count': 'sum',
            'readability_score': 'mean'
        }).reset_index().to_dict('records')
    }
    
    return metrics

def save_metrics(metrics: Dict[str, Any], output_path: str):
    """Save metrics to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Saved metrics to {output_path}")

def main(data_dir: str, output_dir: str, max_workers: int = 4):
    """Main processing function."""
    # Set up the database
    # setup_database()
    
    # Load regulations from cache
    regulations = load_cached_regulations(data_dir)
    
    if not regulations:
        logger.error("No regulations found. Please run the scraper first.")
        return
    
    # Process regulations and calculate metrics
    metrics = process_regulations(regulations, max_workers=max_workers)
    
    # Save metrics to output file
    output_path = os.path.join(output_dir, "metrics.json")
    save_metrics(metrics, output_path)
    
    logger.info("Data processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process eCFR data and calculate metrics")
    parser.add_argument("--data-dir", default="../data", help="Directory containing scraped data")
    parser.add_argument("--output-dir", default="../data", help="Directory to save output")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of worker threads")
    
    args = parser.parse_args()
    
    try:
        main(args.data_dir, args.output_dir, args.max_workers)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        sys.exit(1)