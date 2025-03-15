import Link from 'next/link'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { BarChart, BarChart2, LineChart, ListFilter } from 'lucide-react'

type FeatureHighlightProps = {
  title: string
  description: string
  icon: string
  link: string
}

export default function FeatureHighlight({ title, description, icon, link }: FeatureHighlightProps) {
  const getIcon = () => {
    switch (icon) {
      case 'BarChart':
        return <BarChart2 className="h-14 w-14 text-government" />
      case 'LineChart':
        return <LineChart className="h-14 w-14 text-regulation" />
      case 'ListFilter':
        return <ListFilter className="h-14 w-14 text-government-dark" />
      default:
        return <BarChart className="h-14 w-14 text-government" />
    }
  }

  return (
    <Card className="flex flex-col items-center text-center p-8 shadow-card card-hover transition-all">
      <CardHeader className="pb-2 space-y-4">
        <div className="rounded-full bg-muted p-4 flex items-center justify-center">
          {getIcon()}
        </div>
        <CardTitle className="text-2xl font-bold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="pb-8">
        <CardDescription className="text-base">{description}</CardDescription>
      </CardContent>
      <CardFooter>
        <Button asChild variant="outline" className="rounded-full px-6 border-2 shadow-sm transition-all hover:shadow">
          <Link href={link}>Explore Feature</Link>
        </Button>
      </CardFooter>
    </Card>
  )
}