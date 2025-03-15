#!/usr/bin/env python3

"""
Cloudflare Worker-compatible API for eCFR Analyzer.
This script is designed to be deployed to Cloudflare Workers.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from typing import Dict, Any

app = FastAPI(
    title="eCFR Analyzer API",
    description="Cloudflare Worker API for eCFR Analyzer",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# eCFR API constants
ECFR_API_BASE = "https://www.ecfr.gov/api/versioner/v1"
ECFR_BASE_URL = "https://www.ecfr.gov"

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {
        "status": "online",
        "service": "eCFR Analyzer API",
        "version": "0.1.0"
    }

@app.get("/api/live/titles")
async def get_live_titles():
    """Get the current list of titles directly from eCFR API."""
    try:
        response = requests.get(f"{ECFR_API_BASE}/titles", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from eCFR API: {str(e)}")

@app.get("/api/live/title/{title_number}")
async def get_live_title(title_number: int):
    """Get current data for a specific title."""
    try:
        # First check if title exists
        titles_response = requests.get(f"{ECFR_API_BASE}/titles", timeout=10)
        titles_response.raise_for_status()
        titles_data = titles_response.json()
        
        title_found = False
        title_name = ""
        
        if 'titles' in titles_data:
            for title in titles_data['titles']:
                if title.get('number') == title_number:
                    title_found = True
                    title_name = title.get('name', '')
                    break
        
        if not title_found:
            raise HTTPException(status_code=404, detail=f"Title {title_number} not found")
        
        # Return basic title info
        return {
            "title": {
                "number": title_number,
                "name": title_name
            },
            "source_url": f"{ECFR_BASE_URL}/current/title-{title_number}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching title {title_number}: {str(e)}")

# For Cloudflare Workers compatibility
def handler(request, env):
    """Handle HTTP requests for Cloudflare Workers."""
    # Process the request through FastAPI
    from fastapi.applications import get_response
    
    scope = {
        "type": "http",
        "method": request.method,
        "path": request.url.path,
        "headers": [(k.lower(), v) for k, v in request.headers.items()],
        "query_string": request.url.query,
        "client": ("cloudflare-worker", 0),
        "server": ("cloudflare-worker", 0),
    }
    
    # Add form data if present
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = request.json()
            scope["body"] = json.dumps(body).encode("utf-8")
        except ValueError:
            scope["body"] = b""
    
    # Process request through FastAPI
    response = get_response(app, scope)
    
    # Convert FastAPI response to Cloudflare Worker response
    return Response(
        body=response.body,
        status=response.status_code,
        headers=dict(response.headers),
    )

# Export the handler for Cloudflare Workers
addEventListener("fetch", lambda event: event.respondWith(handler(event.request, event.env)))