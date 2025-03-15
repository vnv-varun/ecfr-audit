# eCFR Analyzer

A web-based tool for analyzing and visualizing the Electronic Code of Federal Regulations (eCFR). This project provides insights into federal regulations through text analysis and data visualization.

## Project Overview

The eCFR Analyzer downloads and processes the Code of Federal Regulations data to generate metrics like word count per agency and visualizes this information through an interactive dashboard. The project pulls data directly from official government sources and makes it accessible through a modern web interface.

### Key Features

- **Data Collection**: Downloads regulation data from the GovInfo Bulk Data Repository
- **Text Analysis**: Calculates basic metrics like word count, section count, and paragraph count
- **Interactive Dashboard**: Visualizes metrics with charts and comparative views
- **Live Data Access**: Connects to the official eCFR API for real-time data
- **Command-Line Tools**: Provides utilities for data processing and management

## Technical Implementation

### Backend (Python)

- **FastAPI**: API server with endpoint definitions
- **Data Processing**: XML parsing and text analysis
- **SQLite Database**: Local data storage for processed information
- **Cloudflare Workers**: Deployment option for the API endpoints

### Frontend (Next.js)

- **Next.js 14**: React framework with App Router
- **Shadcn UI**: Component library with Tailwind CSS
- **Chart.js**: Data visualization for regulatory metrics
- **TypeScript**: Type-safe development

## Analysis and Metrics

The project calculates several metrics to provide insights into federal regulations:

- **Word Count Analysis**: Tracks the total number of words across titles and agencies
- **Section Count**: Measures the number of sections within each regulation title
- **Paragraph Count**: Quantifies content volume by counting paragraphs
- **Comparative Views**: Allows side-by-side comparison between agencies and titles
- **Historical Data**: Shows changes in regulation volume over time (where data is available)

## Project Structure

- `/backend/` - Python backend for data processing and API
  - `/backend/api/` - API server and endpoints
  - `/backend/models/` - Database models
  - `/backend/processors/` - Data processing modules
  - `/backend/processors/bulk/` - Bulk XML data processing 
  - `/backend/utils/` - Utility functions
  - `/backend/bin/` - Command-line tools
  - `/backend/data/` - Storage for processed data
- `/ui/` - Next.js frontend application
- `/data/` - Shared data directory
- `/migrations/` - Database schema and seeds

## Bulk Data Pipeline

The project includes a pipeline for downloading and processing CFR data from the GovInfo Bulk Data Repository.

### Using the Bulk Processor

To download and process all CFR titles:

```bash
backend/bin/ecfr-bulk
```

To process specific titles:

```bash
backend/bin/ecfr-bulk --title 40
# or multiple titles
backend/bin/ecfr-bulk --titles 1,5,10,40
```

To view information about processed data:

```bash
backend/bin/ecfr-bulk --info
backend/bin/ecfr-bulk --show-title 1  # For specific title details
```

To process data and store in the database:

```bash
backend/bin/ecfr-seed
backend/bin/ecfr-seed --info  # View database information
```

### Additional Options

- `--data-dir PATH`: Specify custom data directory (default: ./data)
- `--max-workers N`: Number of parallel workers (default: 2)
- `--force`: Force re-download of XML files
- `--download-only`: Only download XML files without processing

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv backend/venv
   source backend/venv/bin/activate  # On Windows: backend\venv\Scripts\activate
   ```

2. Install dependencies and package:
   ```bash
   pip install -r backend/requirements.txt
   pip install -e backend/
   ```

3. Run the bulk data processor:
   ```bash
   backend/bin/ecfr-bulk
   ```

4. Seed the database:
   ```bash
   backend/bin/ecfr-seed
   ```

5. Start the backend API server:
   ```bash
   python -m backend.api.app
   ```

### Frontend Setup

1. Navigate to the UI directory:
   ```bash
   cd ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Deployment

The project can be deployed using Cloudflare as a hosting service, though it could work with any container system or hosting platform.

### Cloudflare Deployment

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```

2. Create D1 database (if using Cloudflare D1):
   ```bash
   npx wrangler d1 create ecfr-analyzer-db
   ```

3. Update the `wrangler.toml` file with your database ID

4. Apply migrations:
   ```bash
   npx wrangler d1 execute ecfr-analyzer-db --file=./migrations/0001_initial_schema.sql
   npx wrangler d1 execute ecfr-analyzer-db --file=./migrations/0002_sample_data.sql
   ```

5. Deploy the Worker:
   ```bash
   npx wrangler deploy
   ```

6. Deploy the frontend:
   ```bash
   cd ui && npm run build
   npx wrangler pages deploy ui/.next
   ```

## API Endpoints

The system provides API endpoints for accessing regulation data:

### Pre-processed Data
- `/api/titles` - List all CFR titles
- `/api/title/{number}` - Get details for a specific title
- `/api/metrics/word-counts` - Get word count metrics
- `/api/metrics/complexity` - Get complexity metrics
- `/api/search` - Search regulations by keyword

### Live Data
- `/api/live/titles` - Get real-time data from eCFR API
- `/api/live/title/{number}` - Get real-time data for a specific title
- `/api/refresh-data` - Trigger a data refresh (POST)

## License

MIT# ecfr-audit
