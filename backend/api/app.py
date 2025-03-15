#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime

# Import endpoints
from .endpoints.live_data import router as live_data_router
from .endpoints.metrics import router as metrics_router

# Will be implemented later
# from ..models.database import get_db
# from ..models.models import Agency, Title, Regulation
# from ..processors.analyzer import get_word_counts, get_complexity_metrics
# from ..utils.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ecfr_api')

app = FastAPI(
    title="eCFR Analyzer API",
    description="API for analyzing the Electronic Code of Federal Regulations",
    version="0.1.0"
)

# Include routers
app.include_router(live_data_router)
app.include_router(metrics_router, prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "title": "eCFR Analyzer API",
        "version": "0.1.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agencies")
async def get_agencies():
    """Get a list of all agencies."""
    # Placeholder data until DB is set up
    agencies = [
        {"id": "acfr", "name": "Administrative Committee of the Federal Register"},
        {"id": "treasury", "name": "Department of the Treasury"},
        {"id": "doj", "name": "Department of Justice"},
        {"id": "epa", "name": "Environmental Protection Agency"}
    ]
    return {"agencies": agencies}

@app.get("/api/titles")
async def get_titles():
    """Get a list of all titles."""
    # Placeholder data until DB is set up
    titles = [
        {"number": 1, "name": "General Provisions"},
        {"number": 5, "name": "Administrative Personnel"},
        {"number": 10, "name": "Energy"},
        {"number": 40, "name": "Protection of Environment"}
    ]
    return {"titles": titles}

@app.get("/api/metrics/word-counts")
async def get_word_count_metrics(
    agency_id: Optional[str] = None,
    title_number: Optional[int] = None
):
    """Get word count metrics, optionally filtered by agency or title."""
    # Placeholder data until analytics module is implemented
    metrics = {
        "total_word_count": 25000000,
        "agencies": [
            {"id": "acfr", "name": "Administrative Committee of the Federal Register", "word_count": 500000},
            {"id": "treasury", "name": "Department of the Treasury", "word_count": 3500000},
            {"id": "doj", "name": "Department of Justice", "word_count": 4000000},
            {"id": "epa", "name": "Environmental Protection Agency", "word_count": 5000000}
        ],
        "titles": [
            {"number": 1, "name": "General Provisions", "word_count": 300000},
            {"number": 5, "name": "Administrative Personnel", "word_count": 2000000},
            {"number": 10, "name": "Energy", "word_count": 1500000},
            {"number": 40, "name": "Protection of Environment", "word_count": 4500000}
        ]
    }
    
    # Apply filters if provided
    if agency_id:
        metrics["agencies"] = [a for a in metrics["agencies"] if a["id"] == agency_id]
    if title_number:
        metrics["titles"] = [t for t in metrics["titles"] if t["number"] == title_number]
        
    return metrics

@app.get("/api/metrics/complexity")
async def get_complexity_metrics(
    agency_id: Optional[str] = None,
    title_number: Optional[int] = None
):
    """Get complexity metrics, optionally filtered by agency or title."""
    # Placeholder data until analytics module is implemented
    metrics = {
        "average_readability_score": 42.5,  # Flesch-Kincaid (higher is easier to read)
        "average_sentence_length": 25.3,    # words per sentence
        "average_word_length": 5.7,         # characters per word
        "agencies": [
            {"id": "acfr", "name": "Administrative Committee of the Federal Register", "readability_score": 45.2},
            {"id": "treasury", "name": "Department of the Treasury", "readability_score": 38.7},
            {"id": "doj", "name": "Department of Justice", "readability_score": 36.5},
            {"id": "epa", "name": "Environmental Protection Agency", "readability_score": 35.1}
        ],
        "titles": [
            {"number": 1, "name": "General Provisions", "readability_score": 48.3},
            {"number": 5, "name": "Administrative Personnel", "readability_score": 43.1},
            {"number": 10, "name": "Energy", "readability_score": 40.2},
            {"number": 40, "name": "Protection of Environment", "readability_score": 34.8}
        ]
    }
    
    # Apply filters if provided
    if agency_id:
        metrics["agencies"] = [a for a in metrics["agencies"] if a["id"] == agency_id]
    if title_number:
        metrics["titles"] = [t for t in metrics["titles"] if t["number"] == title_number]
        
    return metrics

@app.get("/api/search")
async def search_regulations(
    query: str = Query(..., min_length=3, description="Search query"),
    agency_id: Optional[str] = None,
    title_number: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100)
):
    """Search regulations by keyword, optionally filtered by agency or title."""
    # Placeholder data until search module is implemented
    results = [
        {
            "id": "title-40-part-60",
            "title": "Standards of Performance for New Stationary Sources",
            "agency": "Environmental Protection Agency",
            "content_snippet": "...emissions means the weight of pollutants emitted...",
            "relevance_score": 0.95
        },
        {
            "id": "title-10-part-20",
            "title": "Standards for Protection Against Radiation",
            "agency": "Nuclear Regulatory Commission",
            "content_snippet": "...protection factors for respirators...",
            "relevance_score": 0.82
        }
    ]
    
    # Apply filters if provided
    if agency_id:
        results = [r for r in results if r["agency"].lower().replace(" ", "-") == agency_id]
    if title_number:
        results = [r for r in results if r["id"].startswith(f"title-{title_number}")]
        
    return {"results": results[:limit]}

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run("backend.api.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()