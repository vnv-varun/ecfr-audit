import { NextResponse } from 'next/server'
import * as fs from 'fs'
import * as path from 'path'

export async function GET() {
  try {
    // Path to the summary.json file relative to the project root
    const summaryPath = path.join(process.cwd(), '..', 'data', 'processed', 'summary.json')
    
    // Check if the file exists
    if (!fs.existsSync(summaryPath)) {
      console.error(`Summary file not found at ${summaryPath}`)
      return NextResponse.json(
        { error: 'Summary data not found' },
        { status: 404 }
      )
    }
    
    // Read and parse the JSON file
    const summaryData = JSON.parse(fs.readFileSync(summaryPath, 'utf8'))
    
    // Return the data
    return NextResponse.json(summaryData)
  } catch (error) {
    console.error('Error fetching titles data:', error)
    return NextResponse.json(
      { error: 'Failed to fetch titles data' },
      { status: 500 }
    )
  }
}