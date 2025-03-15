import { NextRequest, NextResponse } from 'next/server'
import { API_BASE_URL } from '@/lib/utils'

// Fallback metrics from the dashboard-metrics component
const FALLBACK_METRICS = {
  wordCounts: {
    total: 94356420, // From summary.json
    byAgency: [
      { name: 'Environmental Protection Agency', count: 13626661, color: '#5470c6' },
      { name: 'Department of the Treasury', count: 11733272, color: '#91cc75' },
      { name: 'Department of Agriculture', count: 5521754, color: '#fac858' },
      { name: 'Department of Labor', count: 3703669, color: '#ee6666' },
      { name: 'Department of Transportation', count: 3569473, color: '#73c0de' },
      { name: 'Department of Health and Human Services', count: 3138221, color: '#3ba272' },
      { name: 'Federal Communications Commission', count: 2243705, color: '#fc8452' },
      { name: 'Federal Acquisition Regulations System', count: 2552943, color: '#9a60b4' },
      { name: 'Department of Commerce', count: 914904, color: '#ea7ccc' },
      { name: 'Department of Justice', count: 809167, color: '#7B68EE' },
      { name: 'Department of Energy', count: 2017288, color: '#FF7F50' },
      { name: 'Department of Defense', count: 1693641, color: '#4682B4' },
      { name: 'Department of Homeland Security', count: 172071, color: '#20B2AA' },
      { name: 'Department of the Interior', count: 1135194, color: '#8FBC8F' },
      { name: 'Department of Housing and Urban Development', count: 1757818, color: '#BC8F8F' },
      { name: 'Department of Veterans Affairs', count: 1238011, color: '#9370DB' },
      { name: 'Department of Education', count: 1166087, color: '#DB7093' },
      { name: 'Nuclear Regulatory Commission', count: 720593, color: '#2E8B57' },
      { name: 'Commodity Futures Trading Commission', count: 2261224, color: '#8B4513' },
      { name: 'Federal Trade Commission', count: 907822, color: '#FF4500' },
      { name: 'Securities and Exchange Commission', count: 1267815, color: '#6495ED' },
      { name: 'Equal Employment Opportunity Commission', count: 1865381, color: '#696969' },
      { name: 'Federal Election Commission', count: 239965, color: '#A0522D' },
      { name: 'Small Business Administration', count: 548488, color: '#C71585' },
      { name: 'Federal Emergency Management Agency', count: 290852, color: '#708090' },
      { name: 'Consumer Financial Protection Bureau', count: 3821431, color: '#00CED1' },
      { name: 'Food and Drug Administration', count: 2754565, color: '#DAA520' },
      { name: 'Bureau of Consumer Financial Protection', count: 1549471, color: '#008B8B' },
      { name: 'National Labor Relations Board', count: 1359066, color: '#9932CC' },
      { name: 'Social Security Administration', count: 2039149, color: '#E9967A' },
      { name: 'National Archives and Records Administration', count: 59648, color: '#FF69B4' },
      { name: 'Office of Personnel Management', count: 311010, color: '#6A5ACD' },
      { name: 'Bureau of Land Management', count: 810861, color: '#00FF7F' },
      { name: 'National Park Service', count: 949167, color: '#6B8E23' },
      { name: 'Fish and Wildlife Service', count: 3534579, color: '#191970' },
      { name: 'Federal Aviation Administration', count: 1726497, color: '#BA55D3' },
      { name: 'Bureau of Indian Affairs', count: 1043712, color: '#CD853F' },
      { name: 'Federal Reserve System', count: 708915, color: '#FFA07A' },
      { name: 'Coast Guard', count: 1835531, color: '#7CFC00' },
      { name: 'Alcohol and Tobacco Tax and Trade Bureau', count: 1019308, color: '#7FFF00' },
      { name: 'Bureau of Alcohol, Tobacco, Firearms, and Explosives', count: 900167, color: '#9ACD32' },
      { name: 'National Institute of Standards and Technology', count: 607114, color: '#66CDAA' },
      { name: 'US Citizenship and Immigration Services', count: 252795, color: '#00FA9A' },
      { name: 'Federal Highway Administration', count: 369083, color: '#556B2F' },
      { name: 'Federal Maritime Commission', count: 66873, color: '#3CB371' },
      { name: 'US Postal Service', count: 1416187, color: '#87CEEB' },
      { name: 'Executive Office of the President', count: 4124, color: '#5F9EA0' },
      { name: 'US Copyright Office', count: 72000, color: '#2F4F4F' },
      { name: 'US Patent and Trademark Office', count: 128000, color: '#ADFF2F' },
      { name: 'National Oceanic and Atmospheric Administration', count: 240000, color: '#B0E0E6' }
    ],
    byTitle: [
      { name: 'Title 40: Protection of Environment', count: 13626661, color: '#5470c6' },
      { name: 'Title 26: Internal Revenue', count: 11733272, color: '#91cc75' },
      { name: 'Title 7: Agriculture', count: 5521754, color: '#fac858' },
      { name: 'Title 29: Labor', count: 3703669, color: '#ee6666' },
      { name: 'Title 49: Transportation', count: 3569473, color: '#73c0de' }
    ]
  },
  complexity: {
    average: 42.5,
    byAgency: [
      { name: 'Environmental Protection Agency', score: 35.1, color: '#5470c6' },
      { name: 'Department of the Treasury', score: 38.7, color: '#91cc75' },
      { name: 'Department of Agriculture', score: 36.5, color: '#fac858' },
      { name: 'Department of Labor', score: 41.2, color: '#ee6666' },
      { name: 'Department of Transportation', score: 39.8, color: '#73c0de' },
      { name: 'Department of Health and Human Services', score: 37.2, color: '#3ba272' },
      { name: 'Federal Communications Commission', score: 43.5, color: '#fc8452' },
      { name: 'Federal Acquisition Regulations System', score: 40.1, color: '#9a60b4' },
      { name: 'Department of Commerce', score: 36.8, color: '#ea7ccc' },
      { name: 'Department of Justice', score: 38.2, color: '#7B68EE' },
      { name: 'Department of Energy', score: 37.8, color: '#FF7F50' },
      { name: 'Department of Defense', score: 39.3, color: '#4682B4' },
      { name: 'Department of Homeland Security', score: 40.7, color: '#20B2AA' },
      { name: 'Department of the Interior', score: 38.4, color: '#8FBC8F' },
      { name: 'Department of Housing and Urban Development', score: 39.6, color: '#BC8F8F' },
      { name: 'Department of Veterans Affairs', score: 42.1, color: '#9370DB' },
      { name: 'Department of Education', score: 41.5, color: '#DB7093' },
      { name: 'Nuclear Regulatory Commission', score: 36.9, color: '#2E8B57' },
      { name: 'Commodity Futures Trading Commission', score: 37.2, color: '#8B4513' },
      { name: 'Federal Trade Commission', score: 43.8, color: '#FF4500' },
      { name: 'Securities and Exchange Commission', score: 42.4, color: '#6495ED' },
      { name: 'Equal Employment Opportunity Commission', score: 44.3, color: '#696969' },
      { name: 'Federal Election Commission', score: 40.8, color: '#A0522D' },
      { name: 'Small Business Administration', score: 45.2, color: '#C71585' },
      { name: 'Federal Emergency Management Agency', score: 38.9, color: '#708090' },
      { name: 'Consumer Financial Protection Bureau', score: 36.7, color: '#00CED1' },
      { name: 'Food and Drug Administration', score: 35.9, color: '#DAA520' },
      { name: 'Bureau of Consumer Financial Protection', score: 37.2, color: '#008B8B' },
      { name: 'National Labor Relations Board', score: 40.6, color: '#9932CC' },
      { name: 'Social Security Administration', score: 41.3, color: '#E9967A' },
      { name: 'National Archives and Records Administration', score: 44.7, color: '#FF69B4' },
      { name: 'Office of Personnel Management', score: 43.1, color: '#6A5ACD' },
      { name: 'Bureau of Land Management', score: 39.4, color: '#00FF7F' },
      { name: 'National Park Service', score: 41.8, color: '#6B8E23' },
      { name: 'Fish and Wildlife Service', score: 38.1, color: '#191970' },
      { name: 'Federal Aviation Administration', score: 37.5, color: '#BA55D3' },
      { name: 'Bureau of Indian Affairs', score: 40.2, color: '#CD853F' },
      { name: 'Federal Reserve System', score: 38.6, color: '#FFA07A' },
      { name: 'Coast Guard', score: 39.1, color: '#7CFC00' },
      { name: 'Alcohol and Tobacco Tax and Trade Bureau', score: 37.9, color: '#7FFF00' }
    ]
  },
  trends: {
    wordCounts: [
      { year: 2020, count: 88000000 },
      { year: 2021, count: 89800000 },
      { year: 2022, count: 91500000 },
      { year: 2023, count: 92800000 },
      { year: 2024, count: 93700000 },
      { year: 2025, count: 94356420 }
    ]
  }
};

export async function GET(request: NextRequest) {
  try {
    // Forward the request to the backend
    const backendUrl = `${API_BASE_URL}/api/metrics`
    console.log(`Attempting to fetch metrics from: ${backendUrl}`);
    console.log(`API_BASE_URL from env: ${process.env.NEXT_PUBLIC_API_URL || 'not set'}`);
    
    // Add a timestamp to avoid caching
    const timestamp = new Date().getTime();
    const urlWithTimestamp = `${backendUrl}?t=${timestamp}`;
    console.log(`Actual request URL with timestamp: ${urlWithTimestamp}`);
    
    try {
      console.log('Sending request with cache busting headers...');
      const response = await fetch(urlWithTimestamp, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        },
        // Use a longer timeout to ensure we get data
        signal: AbortSignal.timeout(15000), // Increased timeout
        // Add cache busting parameter to avoid stale data
        cache: 'no-store',
        next: { revalidate: 0 } // For Next.js 13+ cache control
      })
      
      console.log(`Metrics API response status: ${response.status}`);
      console.log(`Response headers:`, Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        console.warn('Error fetching metrics from backend, using fallback data')
        console.log(`Status code: ${response.status}, Status text: ${response.statusText}`);
        console.log(`Using fallback data with ${FALLBACK_METRICS?.wordCounts?.byAgency?.length || 0} agencies`)
        
        // Try to get more error details
        try {
          const errorText = await response.text();
          console.error('Backend error response:', errorText);
        } catch (e) {
          console.error('Could not read error response');
        }
        
        return NextResponse.json(FALLBACK_METRICS)
      }
      
      try {
        const responseText = await response.text();
        console.log('Raw response (first 200 chars):', responseText.substring(0, 200) + '...');
        
        try {
          const data = JSON.parse(responseText);
          console.log(`Received data from backend API with ${data?.wordCounts?.byAgency?.length || 0} agencies`);
          return NextResponse.json(data);
        } catch (jsonError) {
          console.error('Error parsing JSON:', jsonError);
          console.error('JSON parse error on response:', responseText.substring(0, 500) + '...');
          return NextResponse.json(FALLBACK_METRICS);
        }
      } catch (parseError) {
        console.error('Error reading response text:', parseError);
        return NextResponse.json(FALLBACK_METRICS)
      }
    } catch (fetchError) {
      console.error('Error fetching from backend:', fetchError);
      // Type-safe error logging - handle unknown error type
      if (fetchError instanceof Error) {
        console.log(`Error name: ${fetchError.name}, message: ${fetchError.message}`);
      } else {
        console.log('Unknown error type:', fetchError);
      }
      console.log(`Using fallback data with ${FALLBACK_METRICS?.wordCounts?.byAgency?.length || 0} agencies`);
      return NextResponse.json(FALLBACK_METRICS)
    }
    
  } catch (error) {
    console.error('Error fetching metrics:', error)
    // Return fallback data if the backend is unavailable
    return NextResponse.json(FALLBACK_METRICS)
  }
}