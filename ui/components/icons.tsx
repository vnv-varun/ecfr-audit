import {
  BarChart,
  BookOpenCheck,
  FileText,
  LucideProps,
  Moon,
  SunMedium,
} from "lucide-react"

// Use LucideProps for icon type
export type Icon = React.ForwardRefExoticComponent<
  LucideProps & React.RefAttributes<SVGSVGElement>
>

export const Icons = {
  sun: SunMedium,
  moon: Moon,
  logo: BookOpenCheck,
  barChart: BarChart,
  document: FileText
}