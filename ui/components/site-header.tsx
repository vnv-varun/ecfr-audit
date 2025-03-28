import Link from "next/link"
import { ModeToggle } from "@/components/mode-toggle"
import { Button } from "@/components/ui/button"
import { MainNav } from "@/components/main-nav"

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex flex-col sm:flex-row h-auto sm:h-16 py-3 sm:py-0 items-center">
        <MainNav />
        <div className="flex flex-1 items-center w-full justify-center sm:justify-end space-x-4 mt-4 sm:mt-0">
          <nav className="flex items-center space-x-3">
            <Button variant="outline" asChild>
              <Link href="https://www.ecfr.gov/" target="_blank" rel="noopener noreferrer">
                eCFR Website
              </Link>
            </Button>
            <ModeToggle />
          </nav>
        </div>
      </div>
    </header>
  )
}