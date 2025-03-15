import * as React from "react"

import { cn, formatNumber, formatPercent, formatCompactNumber, formatDate, truncateText, getReadabilityColor, API_BASE_URL } from "@/lib"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

// New collapsible card component
interface CollapsibleCardProps extends React.HTMLAttributes<HTMLDivElement> {
  expanded?: boolean
  onToggle?: () => void
  defaultExpanded?: boolean
}

const CollapsibleCard = React.forwardRef<HTMLDivElement, CollapsibleCardProps>(
  ({ expanded, onToggle, defaultExpanded = false, className, children, ...props }, ref) => {
    const [isExpanded, setIsExpanded] = React.useState(defaultExpanded)
    
    const handleToggle = () => {
      const newState = !isExpanded
      setIsExpanded(newState)
      if (onToggle) onToggle()
    }
    
    // Allow controlled or uncontrolled usage
    const actuallyExpanded = expanded !== undefined ? expanded : isExpanded
    
    return (
      <Card
        ref={ref}
        className={cn(
          "transition-all duration-200",
          actuallyExpanded ? "shadow-md" : "hover:shadow",
          className
        )}
        {...props}
      >
        {React.Children.map(children, child => {
          if (React.isValidElement(child) && child.type === CollapsibleCardTrigger) {
            return React.cloneElement(child, {
              expanded: actuallyExpanded,
              onClick: (e: React.MouseEvent) => {
                handleToggle()
                if (child.props.onClick) child.props.onClick(e)
              }
            } as React.HTMLAttributes<HTMLDivElement> & { expanded?: boolean })
          }
          
          if (React.isValidElement(child) && child.type === CollapsibleCardContent) {
            return React.cloneElement(child, {
              expanded: actuallyExpanded,
            } as React.HTMLAttributes<HTMLDivElement> & { expanded?: boolean })
          }
          
          return child
        })}
      </Card>
    )
  }
)
CollapsibleCard.displayName = "CollapsibleCard"

interface CollapsibleCardTriggerProps extends React.HTMLAttributes<HTMLDivElement> {
  expanded?: boolean
}

const CollapsibleCardTrigger = React.forwardRef<HTMLDivElement, CollapsibleCardTriggerProps>(
  ({ expanded, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "cursor-pointer p-6 flex items-center justify-between",
          className
        )}
        {...props}
      >
        <div className="flex-1">{children}</div>
        <div className="flex items-center justify-center h-6 w-6 rounded-full bg-muted transition-transform duration-200">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={cn(
              "transition-transform duration-200",
              expanded ? "rotate-180" : "rotate-0"
            )}
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
    )
  }
)
CollapsibleCardTrigger.displayName = "CollapsibleCardTrigger"

interface CollapsibleCardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  expanded?: boolean
}

const CollapsibleCardContent = React.forwardRef<HTMLDivElement, CollapsibleCardContentProps>(
  ({ expanded, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "overflow-hidden transition-all duration-200",
          expanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0",
          className
        )}
        {...props}
      >
        <div className="p-6 pt-0">{children}</div>
      </div>
    )
  }
)
CollapsibleCardContent.displayName = "CollapsibleCardContent"

export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent,
  CollapsibleCard,
  CollapsibleCardTrigger,
  CollapsibleCardContent
}