"use client"

import { cn, formatNumber, formatPercent, formatCompactNumber, formatDate, truncateText, getReadabilityColor, API_BASE_URL } from "../utils"
import { useEffect, useState } from "react"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  // Use client-side only rendering to avoid hydration mismatch
  const [isMounted, setIsMounted] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null // Return nothing during SSR
  }

  return (
    <div
      className={cn("animate-pulse rounded-md bg-primary/10", className)}
      {...props}
    />
  )
}

export { Skeleton }