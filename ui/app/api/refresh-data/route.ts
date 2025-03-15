import { NextRequest, NextResponse } from 'next/server'
import { API_BASE_URL } from '@/lib/utils'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Prepare the request parameters
    let queryParams = new URLSearchParams();
    
    // Map frontend entity type to backend parameter
    if (body.entityType === 'title' && body.titleNumber) {
      queryParams.append('entity_type', 'title');
      queryParams.append('entity_id', body.titleNumber.toString());
    } else if (body.entityType === 'agency' && body.agencyName) {
      queryParams.append('entity_type', 'agency');
      queryParams.append('entity_id', body.agencyName.toLowerCase().replace(/\s+/g, '-'));
    } else {
      queryParams.append('entity_type', 'all');
    }
    
    // Add timestamp for cache busting
    queryParams.append('t', Date.now().toString());
    
    // Log what we're sending
    console.log('Sending refresh request with params:', queryParams.toString());
    
    // Forward the request to the backend
    const backendUrl = `${API_BASE_URL}/api/refresh-data?${queryParams.toString()}`
    console.log(`Attempting to connect to backend at: ${backendUrl}`);
    
    try {
      const response = await fetch(backendUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        },
        // Add a short timeout so the UI doesn't block
        signal: AbortSignal.timeout(8000), // Increased timeout
        cache: 'no-store'
      })
      
      console.log(`Backend response status: ${response.status}`);
      
      // Try to get response details even if it's not ok
      const responseText = await response.text();
      try {
        const responseData = JSON.parse(responseText);
        console.log("Response data:", responseData);
        return NextResponse.json(responseData);
      } catch (parseError) {
        console.log("Raw response:", responseText);
        
        // If we couldn't parse JSON, still treat as success if status is ok
        if (response.ok) {
          return NextResponse.json({
            success: true,
            message: "Refresh completed successfully",
            updated_at: new Date().toISOString()
          });
        } else {
          return NextResponse.json(
            { error: `Failed to refresh data: ${responseText}` },
            { status: response.status }
          );
        }
      }
    } catch (fetchError) {
      console.error("Fetch error:", fetchError);
      return NextResponse.json(
        { error: `Failed to connect to backend: ${fetchError.message}` },
        { status: 500 }
      );
    }
    
  } catch (error) {
    console.error('Error refreshing data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}