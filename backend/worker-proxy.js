/**
 * Worker Proxy for eCFR Analyzer API
 * This worker acts as a proxy between Cloudflare and our backend API.
 * Since Python workers are still experimental, we use this JS worker to:
 * 1. Handle incoming requests
 * 2. Access the D1 database 
 * 3. Return responses
 */

// D1 database schema initialization - no longer needed as we have populated the DB
const SCHEMA = "";

// Main request handler
export default {
  async fetch(request, env, ctx) {
    // Parse the URL and pathname
    const url = new URL(request.url);
    const path = url.pathname;
    
    // Initialize database if needed
    await initializeDb(env.DB);
    
    // API endpoints
    if (path === '/') {
      return new Response(JSON.stringify({
        status: "online",
        service: "eCFR Analyzer API",
        version: "0.1.0"
      }), { 
        headers: { 'Content-Type': 'application/json' } 
      });
    }
    
    // Get all titles from D1
    if (path === '/api/titles') {
      try {
        const titles = await env.DB.prepare('SELECT id, number, name, full_name, source_url FROM title ORDER BY number').all();
        return new Response(JSON.stringify(titles.results), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error fetching titles: ${err.message}`);
      }
    }
    
    // Live data from eCFR API
    if (path === '/api/live/titles') {
      try {
        const ecfrResponse = await fetch('https://www.ecfr.gov/api/versioner/v1/titles');
        const data = await ecfrResponse.json();
        return new Response(JSON.stringify(data), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error fetching from eCFR API: ${err.message}`);
      }
    }
    
    // Handle title-specific requests
    const titleMatch = path.match(/^\/api\/title\/(\d+)$/);
    if (titleMatch) {
      const titleNumber = parseInt(titleMatch[1]);
      try {
        const title = await env.DB.prepare(
          'SELECT id, number, name, full_name, source_url FROM title WHERE number = ?'
        ).bind(titleNumber).first();
        
        if (!title) {
          return errorResponse(`Title ${titleNumber} not found`, 404);
        }
        
        // Get metrics for this title
        const metrics = await env.DB.prepare(
          'SELECT word_count, section_count, paragraph_count FROM regulation_metrics WHERE title_id = ?'
        ).bind(title.id).first();
        
        // Combine title and metrics
        const response = {
          ...title,
          metrics: metrics || { word_count: 0, section_count: 0, paragraph_count: 0 }
        };
        
        return new Response(JSON.stringify(response), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error fetching title ${titleNumber}: ${err.message}`);
      }
    }
    
    // Handle live title-specific requests
    const liveTitleMatch = path.match(/^\/api\/live\/title\/(\d+)$/);
    if (liveTitleMatch) {
      const titleNumber = parseInt(liveTitleMatch[1]);
      try {
        // First check if title exists
        const titlesResponse = await fetch('https://www.ecfr.gov/api/versioner/v1/titles');
        const titlesData = await titlesResponse.json();
        
        let titleFound = false;
        let titleName = "";
        
        if (titlesData.titles) {
          for (const title of titlesData.titles) {
            if (title.number === titleNumber) {
              titleFound = true;
              titleName = title.name || '';
              break;
            }
          }
        }
        
        if (!titleFound) {
          return errorResponse(`Title ${titleNumber} not found`, 404);
        }
        
        // Return basic title info
        return new Response(JSON.stringify({
          title: {
            number: titleNumber,
            name: titleName
          },
          source_url: `https://www.ecfr.gov/current/title-${titleNumber}`
        }), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error fetching title ${titleNumber}: ${err.message}`);
      }
    }
    
    // Handle metrics requests
    if (path === '/api/metrics/word-counts') {
      try {
        const metrics = await env.DB.prepare(
          `SELECT t.number as title_number, t.name as title_name, m.word_count 
           FROM regulation_metrics m 
           JOIN title t ON m.title_id = t.id
           ORDER BY m.word_count DESC`
        ).all();
        
        return new Response(JSON.stringify(metrics.results), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error fetching metrics: ${err.message}`);
      }
    }
    
    // API Refresh endpoint
    if (path === '/api/refresh-data' && request.method === 'POST') {
      try {
        // Get request body
        const { titleNumber } = await request.json();
        
        // In a real implementation, this would trigger a background process
        // to update the data from eCFR. For now, we return a message with the title info.
        const title = await env.DB.prepare(
          'SELECT id, number, name FROM title WHERE number = ?'
        ).bind(titleNumber || 1).first();
        
        // Simulate data refresh
        await new Promise(resolve => setTimeout(resolve, 100));
        
        return new Response(JSON.stringify({
          success: true,
          message: `Data refresh for ${title ? title.name : `Title ${titleNumber || 1}`} has been scheduled`,
          title: title || null
        }), { 
          headers: { 'Content-Type': 'application/json' } 
        });
      } catch (err) {
        return errorResponse(`Error scheduling refresh: ${err.message}`);
      }
    }
    
    // Default 404 response
    return new Response(JSON.stringify({
      error: "Not found",
      message: `Endpoint ${path} not found`
    }), { 
      status: 404,
      headers: { 'Content-Type': 'application/json' } 
    });
  }
};

// Helper functions
async function initializeDb(db) {
  // Tables are already created, but we can add indexes for performance
  try {
    await db.exec(`
      CREATE INDEX IF NOT EXISTS idx_title_number ON title(number);
      CREATE INDEX IF NOT EXISTS idx_regulation_metrics_title_id ON regulation_metrics(title_id);
    `);
  } catch (e) {
    // Ignore errors - indexes might already exist
  }
}

function errorResponse(message, status = 500) {
  return new Response(JSON.stringify({
    error: message
  }), { 
    status: status,
    headers: { 'Content-Type': 'application/json' } 
  });
}