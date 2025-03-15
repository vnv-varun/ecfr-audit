#!/usr/bin/env python3

"""
Main entry point for the eCFR Analyzer backend.
This provides a command-line interface to run different components.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ecfr_analyzer')

def setup_parser() -> argparse.ArgumentParser:
    """Set up the command line argument parser."""
    parser = argparse.ArgumentParser(
        description='eCFR Analyzer - Tool to analyze Electronic Code of Federal Regulations'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start API server
    api_parser = subparsers.add_parser('api', help='Start the API server')
    api_parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind the server to'
    )
    api_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind the server to'
    )
    
    # Scrape data from eCFR
    scrape_parser = subparsers.add_parser('scrape', help='Scrape data from eCFR')
    scrape_parser.add_argument(
        'title_number',
        type=int,
        help='The title number to scrape (1-50)'
    )
    scrape_parser.add_argument(
        '--output-dir',
        type=str,
        default='./data',
        help='Directory to save scraped data'
    )
    
    # Process data and compute metrics
    process_parser = subparsers.add_parser('process', help='Process data and compute metrics')
    process_parser.add_argument(
        '--data-dir',
        type=str,
        default='./data',
        help='Directory containing scraped data'
    )
    process_parser.add_argument(
        '--output-dir',
        type=str,
        default='./data',
        help='Directory to save processed data'
    )
    
    # Seed database
    seed_parser = subparsers.add_parser('seed', help='Seed database from scraped data')
    seed_parser.add_argument(
        '--data-dir',
        type=str,
        default='./data',
        help='Directory containing scraped data'
    )
    seed_parser.add_argument(
        '--db-path',
        type=str,
        default='./data/ecfr.db',
        help='Path to SQLite database'
    )
    
    # Display info about database or data
    info_parser = subparsers.add_parser('info', help='Display information about data')
    info_parser.add_argument(
        '--db-path',
        type=str,
        default='./data/ecfr.db',
        help='Path to SQLite database'
    )
    
    return parser

def main() -> int:
    """Main entry point for the application."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == 'api':
        try:
            from backend.api.app import start_server
            start_server(host=args.host, port=args.port)
        except ImportError:
            # Alternative import path
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from backend.api.app import start_server
            start_server(host=args.host, port=args.port)
        return 0
        
    elif args.command == 'scrape':
        try:
            from backend.processors.scraper import scrape_title
            result = scrape_title(args.title_number, args.output_dir)
            
            if result.get("success", False):
                logger.info(f"Successfully scraped Title {args.title_number}")
                logger.info(f"Sections: {result.get('sections_count', 0)}")
                return 0
            else:
                logger.error(f"Failed to scrape Title {args.title_number}: {result.get('error')}")
                return 1
        except ImportError:
            # Fallback to original scraper if needed
            logger.info("Using original scraper module")
            from ecfr.core.title_scraper import scrape_single_title
            success = scrape_single_title(args.title_number, args.output_dir)
            return 0 if success else 1
        
    elif args.command == 'process':
        try:
            from backend.processors.process_data import main as process_main
            process_main(args.data_dir, args.output_dir)
            return 0
        except ImportError:
            logger.error("Process module not found")
            return 1
        
    elif args.command == 'seed':
        try:
            from backend.processors.seed_database import main as seed_main
            seed_main()
            return 0
        except ImportError:
            logger.error("Seed database module not found")
            return 1
        
    elif args.command == 'info':
        try:
            import sqlite3
            conn = sqlite3.connect(args.db_path)
            c = conn.cursor()
            
            # Get basic counts
            c.execute("SELECT COUNT(*) FROM agency")
            agency_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM title")
            title_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM regulation")
            regulation_count = c.fetchone()[0]
            
            print(f"Database: {args.db_path}")
            print(f"Agencies: {agency_count}")
            print(f"Titles: {title_count}")
            print(f"Regulations: {regulation_count}")
            
            conn.close()
            return 0
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return 1
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())