# eCFR Analyzer Frontend

The frontend component for the eCFR Analyzer project, providing an interactive web interface for visualizing and exploring federal regulation data.

## Features

- **Interactive Dashboard**: Visual overview of regulation metrics
- **Title Explorer**: Browse and search through regulation titles
- **Comparative Analysis**: Compare metrics across different agencies and titles
- **Data Visualization**: Charts and graphs for regulatory metrics
- **Live Data Integration**: Real-time access to the latest eCFR data

## Technology Stack

- **Next.js 14**: React framework with App Router architecture
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn UI**: Component library based on Radix UI
- **Chart.js**: Data visualization library
- **React Query**: Data fetching and state management

## Directory Structure

- `/app/` - Next.js App Router pages and layouts
  - `/app/api/` - API route handlers
  - `/app/dashboard/` - Dashboard page
  - `/app/titles/` - Titles explorer page
  - `/app/page.tsx` - Home page
  - `/app/layout.tsx` - Root layout
- `/components/` - Reusable UI components
  - `/components/ui/` - Base UI components from Shadcn
  - `/components/dashboard-metrics.tsx` - Dashboard metric components
  - `/components/title-card.tsx` - Title display component
- `/lib/` - Utility functions and shared code

## Visualizations and Components

The frontend includes several key visualizations to make regulatory data accessible:

- **Word Count Bar Charts**: Visualize word count across titles and agencies
- **Title Cards**: Interactive cards showing metrics for each regulation title
- **Metric Summaries**: Aggregated data cards with key statistics
- **Data Tables**: Structured display of detailed metrics
- **Refresh Controls**: Interface for triggering data updates

## Setup and Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Start the production server:
   ```bash
   npm start
   ```

## API Integration

The frontend connects to the backend API to fetch processed regulation data. The main API endpoints used are:

- `/api/titles` - Gets the list of all CFR titles
- `/api/title/{number}` - Gets details for a specific title
- `/api/metrics/word-counts` - Gets word count metrics
- `/api/metrics/complexity` - Gets complexity metrics

For live data access, the frontend uses:

- `/api/live/titles` - Gets real-time list of titles from the eCFR API
- `/api/refresh-data` - Triggers a backend data refresh

## Deployment

The frontend can be deployed to Cloudflare Pages or any static hosting service:

### Cloudflare Pages Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy using Wrangler:
   ```bash
   npx wrangler pages deploy .next
   ```

## Development Notes

- Run type checking: `npm run type-check`
- Run linting: `npm run lint`
- Test API connections: `npm run test-api`