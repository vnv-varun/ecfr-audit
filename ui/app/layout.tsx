import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import SiteHeader from '@/components/site-header'
import { Toaster } from '@/components/ui/toaster'
import { useEffect } from 'react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'eCFR Analyzer - Federal Regulations Dashboard',
  description: 'Analyze and visualize metrics from the Electronic Code of Federal Regulations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Force refresh of styles */}
        <meta httpEquiv="x-ua-compatible" content="ie=edge" />
      </head>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="relative min-h-screen flex flex-col">
            <SiteHeader />
            <div className="flex-1">
              {children}
            </div>
            <footer className="border-t py-6 md:py-0">
              <div className="container flex flex-col items-center justify-between gap-3 py-4 sm:h-16 sm:py-0 sm:flex-row">
                <p className="text-sm text-muted-foreground">
                  &copy; {new Date().getFullYear()} eCFR Analyzer. All rights reserved.
                </p>
                <p className="text-sm text-muted-foreground">
                  Data from <a href="https://www.ecfr.gov/" className="underline" target="_blank" rel="noopener noreferrer">Electronic Code of Federal Regulations</a>
                </p>
              </div>
            </footer>
          </div>
          <Toaster />
        </ThemeProvider>
        
        {/* Debugging script to check if Tailwind is loaded */}
        <script dangerouslySetInnerHTML={{
          __html: `
            document.addEventListener('DOMContentLoaded', function() {
              console.log("Styles loaded");
              const stylesActive = document.querySelector('.container')?.classList.contains('container');
              console.log("Tailwind active:", stylesActive);
            });
          `
        }} />
      </body>
    </html>
  )
}