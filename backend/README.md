# eCFR Analyzer Backend

The backend component for the eCFR Analyzer project, providing functionality for downloading, processing, and analyzing the Electronic Code of Federal Regulations (eCFR) data.

## Features

- **Data Collection**: Downloads XML data from the GovInfo Bulk Data Repository
- **Text Analysis**: Extracts and calculates metrics like word count, section count, and paragraph count
- **Data Storage**: Processes and stores regulation data in SQLite database
- **API Endpoints**: Provides access to processed data and metrics
- **CLI Tools**: Command-line utilities for data processing and management

## Directory Structure

- `/api/` - API server and endpoint definitions
  - `/api/endpoints/` - API route handlers
  - `/api/cloudflare_worker.py` - Cloudflare Workers integration
- `/models/` - Database models and connection handling
- `/processors/` - Data processing modules
  - `/processors/bulk/` - Specialized modules for bulk XML processing
  - `/processors/analyzer.py` - Text analysis functionality
- `/utils/` - Shared utility functions
- `/bin/` - Command-line tools
- `/data/` - Data storage directory
  - `/data/xml/` - Downloaded XML files
  - `/data/processed/` - Processed JSON data
  - `/data/cache/` - Cached responses

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Command-Line Tools

The backend provides several command-line tools for working with eCFR data:

#### Download and Process Bulk Data

```bash
bin/ecfr-bulk [options]
```

Options:
- `--data-dir DIR` - Data directory (default: ./data)
- `--title NUM` - Process a specific title only
- `--titles 1,3,5` - Process multiple specific titles
- `--force` - Force redownload even if files exist
- `--download-only` - Only download files without processing
- `--info` - Display information about processed data
- `--show-title NUM` - Display details for a specific processed title
- `--max-workers N` - Number of parallel workers (default: 2)

#### Process and Store in Database

```bash
bin/ecfr-seed [options]
```

Options:
- `--data-dir DIR` - Data directory (default: ./data)
- `--title NUM` - Process a specific title only
- `--titles 1,3,5` - Process multiple specific titles
- `--info` - Display information about database content

### API Server

Start the API server:

```bash
python -m backend.api.app
```

This launches a FastAPI server with endpoints for accessing processed regulation data.

## Data Processing

The backend implements a multi-step data processing pipeline:

1. **Download**: XML files are downloaded from the GovInfo Bulk Data Repository
2. **Parsing**: XML data is parsed and structured
3. **Analysis**: Basic metrics are calculated for each regulation
4. **Storage**: Processed data is stored in both JSON files and a SQLite database

### Analysis Metrics

The backend calculates several metrics for regulations:

- **Word Count**: Total number of words in each title and section
- **Section Count**: Number of sections within each title
- **Paragraph Count**: Number of paragraphs within each title and section
- **Structure Analysis**: Hierarchical breakdown of regulation organization

## API Endpoints

The API server provides the following endpoints:

- `/api/titles` - List all CFR titles
- `/api/title/{number}` - Get details for a specific title
- `/api/metrics/word-counts` - Get word count metrics
- `/api/metrics/complexity` - Get complexity metrics
- `/api/search` - Search regulations by keyword

### Live Data Integration

The API also provides endpoints for accessing live data from the official eCFR API:

- `/api/live/titles` - Get real-time list of titles
- `/api/live/title/{number}` - Get real-time data for a specific title
- `/api/refresh-data` - Trigger a data refresh (POST)

## Deployment

The backend can be deployed as a standard Python application or using Cloudflare Workers:

### Standard Deployment

Run the FastAPI server using a WSGI server like Uvicorn:

```bash
uvicorn backend.api.app:app --host 0.0.0.0 --port 8000
```

### Cloudflare Deployment

Deploy using Wrangler CLI:

```bash
npx wrangler deploy
```

The `wrangler.toml` configuration uses `worker-proxy.js` as a proxy for the Python backend.

## Development

- Run tests: `python -m pytest`
- Lint code: `flake8 .`
- Type check: `mypy .`