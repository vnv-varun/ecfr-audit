#!/usr/bin/env python3

import os
from pydantic_settings import BaseSettings
from typing import Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('config')

class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    
    # API configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "eCFR Analyzer"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/ecfr.db"
    
    # eCFR API
    ECFR_API_URL: str = "https://www.ecfr.gov/api/versioner/v1"
    ECFR_BASE_URL: str = "https://www.ecfr.gov"
    
    # API rate limiting
    API_RATE_LIMIT: int = 60  # requests per minute
    API_DELAY: float = 1.0  # seconds between requests
    
    # Cache configuration
    CACHE_DIR: str = "./data/cache"
    USE_CACHE: bool = True
    
    # Processing options
    MAX_WORKERS: int = 4  # parallel workers for processing
    PROCESS_METRICS: bool = True  # calculate metrics during processing
    
    # NLP options
    NLTK_DATA_PATH: Optional[str] = None
    SPACY_MODEL: str = "en_core_web_sm"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()

# Ensure paths exist
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)

# Log settings values
logger.info(f"Using database at {settings.DATABASE_URL}")
logger.info(f"eCFR API URL: {settings.ECFR_API_URL}")
logger.info(f"Using cache: {settings.USE_CACHE}")
logger.info(f"Parallelism: {settings.MAX_WORKERS} workers")