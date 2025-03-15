"use client"

import { Button } from "./ui/button"
import { RefreshCw } from "lucide-react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "./ui/use-toast"

interface RefreshButtonProps {
  titleNumber?: number
  agencyName?: string
  entityType?: 'agency' | 'title' | 'all'
  className?: string
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive'
  iconOnly?: boolean
  onRefreshComplete?: () => void
}

export function RefreshButton({ 
  titleNumber, 
  agencyName, 
  entityType = 'all', 
  className = '',
  variant = 'outline',
  iconOnly = false,
  onRefreshComplete
}: RefreshButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleRefresh = async (e: React.MouseEvent) => {
    // Prevent event from bubbling to parent elements
    e.stopPropagation();
    
    setIsLoading(true)
    try {
      // Prepare the request payload based on what we're refreshing
      const payload: any = { entityType: entityType };
      
      if (entityType === 'title' && titleNumber) {
        payload.titleNumber = titleNumber;
      } else if (entityType === 'agency' && agencyName) {
        payload.agencyName = agencyName;
      }
      
      // Send the refresh request with the appropriate payload
      
      // Call the API endpoint to trigger a refresh
      const response = await fetch('/api/refresh-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
      
      if (response.ok) {
        // Show appropriate success toast based on entity type
        let description;
        if (entityType === 'title') {
          description = `Fetching latest data for Title ${titleNumber}. This may take a moment.`;
        } else if (entityType === 'agency') {
          description = `Fetching latest data for ${agencyName}. This may take a moment.`;
        } else {
          description = "Fetching latest data for all metrics. This may take several minutes.";
        }
        
        toast({
          title: "Refresh Started",
          description,
          duration: 5000,
        })
        
        // Wait briefly to allow background process to start
        setTimeout(() => {
          // Refresh the page data
          router.refresh()
          
          // Call the callback if provided
          if (onRefreshComplete) {
            onRefreshComplete();
          }
        }, 1000)
      } else {
        // Show error toast
        const errorData = await response.json()
        console.error("Refresh API error:", errorData);
        toast({
          title: "Refresh Failed",
          description: errorData.error || errorData.detail || "An error occurred while refreshing data.",
          variant: "destructive",
          duration: 5000,
        })
      }
    } catch (error) {
      console.error('Failed to refresh data:', error)
      toast({
        title: "Refresh Failed",
        description: "Could not connect to the server. Please try again later.",
        variant: "destructive",
        duration: 5000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Button 
      onClick={handleRefresh} 
      disabled={isLoading}
      variant={variant}
      size="sm"
      className={`${className} ${iconOnly ? 'p-1 h-6 w-6' : 'px-2'} ${variant === 'outline' ? 'bg-government/10 border-government/20 text-government hover:bg-government/20 hover:text-government' : ''}`}
    >
      <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''} ${iconOnly ? '' : 'mr-1'}`} />
      {!iconOnly && <span className="text-xs">Refresh</span>}
    </Button>
  )
}