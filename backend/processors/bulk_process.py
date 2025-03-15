#!/usr/bin/env python3

"""
Command line interface for bulk processing eCFR data.
"""

import os
import sys
import argparse
import logging

from .bulk import (
    download_title, 
    process_all_titles, 
    display_title_info, 
    display_summary
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bulk_cli')

def main():
    """Main entry point for the processor."""
    parser = argparse.ArgumentParser(description="Download and process eCFR data from GovInfo bulk XML")
    parser.add_argument("--data-dir", default="./data", help="Base directory for data storage")
    parser.add_argument("--max-workers", type=int, default=2, help="Maximum number of parallel workers")
    parser.add_argument("--title", type=int, help="Process a specific title only")
    parser.add_argument("--titles", type=str, help="Comma-separated list of titles to process")
    parser.add_argument("--force", action="store_true", help="Force download even if files exist")
    parser.add_argument("--download-only", action="store_true", help="Only download XML files without processing")
    parser.add_argument("--info", action="store_true", help="Display information about processed titles")
    parser.add_argument("--show-title", type=int, help="Display information about a specific title")
    
    args = parser.parse_args()
    
    # Define directories
    data_dir = args.data_dir
    xml_dir = os.path.join(data_dir, "xml")
    
    # Create directories
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(xml_dir, exist_ok=True)
    
    # Info mode
    if args.info:
        display_summary(data_dir)
        return 0
    
    # Show specific title
    if args.show_title:
        display_title_info(args.show_title, data_dir)
        return 0
    
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
        from .bulk.downloader import TITLE_NAMES
        
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
    
    # Process titles
    results = process_all_titles(
        data_dir=data_dir,
        max_workers=args.max_workers,
        force_download=args.force,
        title_nums=title_nums
    )
    
    if results:
        print("\nProcess completed successfully!")
        print(f"Processed {len(results)} titles.")
        
        # Display summary
        display_summary(data_dir)
        return 0
    else:
        print("\nProcess failed: No titles were successfully processed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())