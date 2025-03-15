import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
 
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ecfr-analyzer-api.vnv-varun.workers.dev'

// Format number with commas
export function formatNumber(num: number) {
  return new Intl.NumberFormat().format(num)
}

// Format percentage
export function formatPercent(num: number) {
  return `${num.toFixed(1)}%`
}

// Format large numbers with K/M/B suffix
export function formatCompactNumber(num: number) {
  if (num < 1000) {
    return num.toString()
  } else if (num < 1000000) {
    return `${(num / 1000).toFixed(1)}K`
  } else if (num < 1000000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else {
    return `${(num / 1000000000).toFixed(1)}B`
  }
}

// Format date
export function formatDate(dateString: string) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

// Truncate text
export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
}

// Get color based on readability score
export function getReadabilityColor(score: number) {
  // Flesch Reading Ease score
  // 90-100: Very Easy
  // 80-89: Easy
  // 70-79: Fairly Easy
  // 60-69: Standard
  // 50-59: Fairly Difficult
  // 30-49: Difficult
  // 0-29: Very Difficult
  
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 60) return 'text-emerald-600 dark:text-emerald-400'
  if (score >= 50) return 'text-yellow-600 dark:text-yellow-400'
  if (score >= 30) return 'text-orange-600 dark:text-orange-400'
  return 'text-red-600 dark:text-red-400'
}