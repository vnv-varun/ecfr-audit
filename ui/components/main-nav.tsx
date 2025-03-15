"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn, formatNumber, formatPercent, formatCompactNumber, formatDate, truncateText, getReadabilityColor, API_BASE_URL } from "@/lib"
import { Icons } from "@/components/icons"

export function MainNav() {
  const pathname = usePathname()

  return (
    <div className="mr-4 flex flex-col md:flex-row items-start md:items-center">
      <Link href="/" className="mr-6 flex items-center space-x-2">
        <Icons.logo className="h-6 w-6" />
        <span className="font-bold inline-block">eCFR Analyzer</span>
      </Link>
      {/* Navigation links have been removed as requested */}
      <nav className="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6 text-sm font-medium mt-2 md:mt-0">
        {/* Empty nav - Dashboard and Titles links removed */}
      </nav>
    </div>
  )
}