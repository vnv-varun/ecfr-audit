"""
Bulk data processing module for downloading and processing eCFR data
from the GovInfo Bulk Data Repository.
"""

from .downloader import download_title
from .processor import extract_text_from_xml, generate_summary
from .pipeline import process_all_titles, display_title_info, display_summary

__all__ = [
    'download_title',
    'extract_text_from_xml',
    'generate_summary',
    'process_all_titles',
    'display_title_info',
    'display_summary'
]