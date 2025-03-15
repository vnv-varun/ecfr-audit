"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn, formatNumber, formatPercent, formatCompactNumber, formatDate, truncateText, getReadabilityColor, API_BASE_URL } from "./utils"
import { Icons } from "@/components/icons"

export function MainNav() {
  const pathname = usePathname()

  return (
    <div className="flex w-full sm:w-auto flex-row items-center justify-center sm:justify-start">
      <Link href="/" className="flex items-center space-x-2">
        <Icons.logo className="h-6 w-6" />
        <span className="font-bold inline-block">eCFR Analyzer</span>
      </Link>
      {/* Navigation links have been removed as requested */}
      <nav className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-6 text-sm font-medium mt-2 sm:mt-0">
        {/* Empty nav - Dashboard and Titles links removed */}
      </nav>
    </div>
  )
}