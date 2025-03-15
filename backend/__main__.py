#!/usr/bin/env python3

"""
Main entry point for the eCFR Analyzer backend.
"""

import argparse
import logging
import sys
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
    
    # Process data
    process_parser = subparsers.add_parser('process', help='Process eCFR data')
    process_parser.add_argument(
        '--data-dir',
        type=str,
        default=str(Path(__file__).parent.parent / 'data'),
        help='Directory containing scraped data'
    )
    process_parser.add_argument(
        '--output-dir',
        type=str,
        default=str(Path(__file__).parent.parent / 'data'),
        help='Directory to save output'
    )
    process_parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of worker threads'
    )
    
    # Scrape eCFR
    scrape_parser = subparsers.add_parser('scrape', help='Scrape the eCFR')
    scrape_parser.add_argument(
        '--output-dir',
        type=str,
        default=str(Path(__file__).parent.parent / 'data'),
        help='Directory to save scraped data'
    )
    scrape_parser.add_argument(
        '--max-titles',
        type=int,
        help='Maximum number of titles to scrape'
    )
    
    # Check eCFR API
    subparsers.add_parser('check-api', help='Check the eCFR API structure')
    
    return parser

def main() -> int:
    """Main entry point for the application."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == 'api':
        # Import here to avoid circular imports
        from .api.app import start_api_server
        return start_api_server(host=args.host, port=args.port)
    
    elif args.command == 'process':
        # Import here to avoid circular imports
        from .processors.process_data import main as process_main
        process_main(args.data_dir, args.output_dir, args.max_workers)
        return 0
    
    elif args.command == 'scrape':
        # Import existing scraper
        from ecfr.core.scraper import ECFRScraper
        
        scraper = ECFRScraper(args.output_dir)
        scraper.scrape(max_titles=args.max_titles)
        return 0
    
    elif args.command == 'check-api':
        # Import existing API checker
        from ecfr.core.api_checker import check_ecfr_api
        
        check_ecfr_api()
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())