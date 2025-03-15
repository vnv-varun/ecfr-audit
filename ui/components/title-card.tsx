"use client"

import * as React from "react"
import {
  CollapsibleCard,
  CollapsibleCardTrigger,
  CollapsibleCardContent,
  CardDescription
} from "@/components/ui/card"
import { BarChart, LineChart, PieChart } from "@/components/ui/charts"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Book, BarChart2, LineChart as LineChartIcon, CircleHelp, BookOpen } from "lucide-react"
import { formatCompactNumber } from "@/lib/utils"

export interface TitleData {
  number: number
  name: string
  wordCount: number
  complexity: number
  yearlyData?: Array<{year: number, wordCount: number}>
  agencies?: Array<{name: string, percentage: number}>
  description?: string
}

interface TitleCardProps {
  title: TitleData
  onViewDetails?: (title: TitleData) => void
}

export function TitleCard({ title, onViewDetails }: TitleCardProps) {
  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(title)
    }
  }

  const getComplexityColor = (score: number) => {
    if (score < 30) return "text-green-600 dark:text-green-400"
    if (score < 40) return "text-amber-600 dark:text-amber-400"
    return "text-red-600 dark:text-red-400"
  }

  const getComplexityLabel = (score: number) => {
    if (score < 30) return "Low"
    if (score < 40) return "Moderate"
    return "High"
  }

  return (
    <CollapsibleCard className="w-full">
      <CollapsibleCardTrigger>
        <div className="flex items-center space-x-4">
          <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-government/10 dark:bg-government/20">
            <Book className="h-6 w-6 text-government" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold leading-none tracking-tight">
                Title {title.number}: {title.name}
              </h3>
              <Badge variant="outline" className="ml-2">
                {formatCompactNumber(title.wordCount)} words
              </Badge>
            </div>
            <CardDescription className="line-clamp-1">
              {title.description || `Federal regulations related to ${title.name}`}
            </CardDescription>
          </div>
        </div>
      </CollapsibleCardTrigger>
      <CollapsibleCardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">
              <BookOpen className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="trends">
              <LineChartIcon className="h-4 w-4 mr-2" />
              Historical Trends
            </TabsTrigger>
            <TabsTrigger value="distribution">
              <PieChart className="h-4 w-4 mr-2" />
              Agency Distribution
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="pt-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-muted/50 p-4 rounded-lg">
                <div className="text-sm text-muted-foreground mb-2">Word Count</div>
                <div className="text-2xl font-bold">{formatCompactNumber(title.wordCount)}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {title.wordCount > 1000000 ? "Large corpus" : title.wordCount > 500000 ? "Medium corpus" : "Small corpus"}
                </div>
              </div>
              
              <div className="bg-muted/50 p-4 rounded-lg">
                <div className="text-sm text-muted-foreground mb-2">Complexity Score</div>
                <div className={`text-2xl font-bold ${getComplexityColor(title.complexity)}`}>
                  {title.complexity.toFixed(1)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {getComplexityLabel(title.complexity)} complexity level
                </div>
              </div>
            </div>

            <div className="mt-4">
              <Button onClick={handleViewDetails} className="w-full">
                View Full Details
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="trends" className="pt-4">
            <div className="h-[200px]">
              {title.yearlyData ? (
                <LineChart
                  data={{
                    labels: title.yearlyData.map(d => d.year.toString()),
                    datasets: [
                      {
                        label: 'Word Count',
                        data: title.yearlyData.map(d => d.wordCount / 1000),
                        borderColor: 'hsl(var(--government))',
                        backgroundColor: 'hsl(var(--government) / 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'hsl(var(--government))',
                        pointBorderColor: '#fff',
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        tension: 0.2,
                        fill: true
                      }
                    ]
                  }}
                  options={{
                    scales: {
                      y: {
                        title: {
                          display: true,
                          text: 'Words (thousands)'
                        }
                      }
                    }
                  }}
                />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-muted-foreground flex flex-col items-center">
                    <CircleHelp className="h-8 w-8 mb-2 opacity-50" />
                    <p>No historical data available</p>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="distribution" className="pt-4">
            <div className="h-[200px]">
              {title.agencies && title.agencies.length > 0 ? (
                <PieChart
                  data={{
                    labels: title.agencies.map(a => a.name),
                    datasets: [
                      {
                        label: 'Agency Distribution',
                        data: title.agencies.map(a => a.percentage),
                        backgroundColor: [
                          'rgba(17, 46, 81, 0.8)',
                          'rgba(208, 74, 2, 0.8)',
                          'rgba(25, 113, 194, 0.8)',
                          'rgba(247, 127, 0, 0.8)',
                          'rgba(71, 130, 160, 0.8)',
                          'rgba(144, 190, 109, 0.8)',
                        ],
                        borderColor: '#fff',
                        borderWidth: 1,
                      }
                    ]
                  }}
                />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-muted-foreground flex flex-col items-center">
                    <CircleHelp className="h-8 w-8 mb-2 opacity-50" />
                    <p>No agency distribution data available</p>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CollapsibleCardContent>
    </CollapsibleCard>
  )
}