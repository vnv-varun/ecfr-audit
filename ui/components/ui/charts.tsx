"use client"

import React, { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
)

// Detect if we're on the client side
const isClient = typeof window !== 'undefined'

// Helper function to detect mobile screens
const isMobileScreen = () => {
  return isClient && window.innerWidth < 640
}

// Common options for all chart types
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  devicePixelRatio: 2, // Higher resolution for mobile
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        font: {
          family: 'Inter, system-ui, sans-serif',
          size: isMobileScreen() ? 10 : 12
        },
        padding: isMobileScreen() ? 10 : 20,
        usePointStyle: true,
        boxWidth: isMobileScreen() ? 6 : 8
      }
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      titleColor: '#000',
      titleFont: {
        size: 14,
        weight: 'bold' as const,
        family: 'Inter, system-ui, sans-serif'
      },
      bodyColor: '#666',
      bodyFont: {
        family: 'Inter, system-ui, sans-serif',
        size: 12
      },
      borderColor: 'rgba(0, 0, 0, 0.1)',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
    },
  },
  interaction: {
    mode: 'nearest' as const,
    axis: 'x' as const,
    intersect: false,
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          family: 'Inter, system-ui, sans-serif',
          size: isMobileScreen() ? 9 : 12
        },
        color: '#666',
        padding: isMobileScreen() ? 4 : 8,
        maxRotation: isMobileScreen() ? 45 : 0,
        autoSkip: true,
        maxTicksLimit: isMobileScreen() ? 6 : 12
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
      border: {
        display: false
      },
      ticks: {
        font: {
          family: 'Inter, system-ui, sans-serif',
          size: isMobileScreen() ? 9 : 12
        },
        color: '#666',
        padding: isMobileScreen() ? 4 : 8,
        maxTicksLimit: isMobileScreen() ? 5 : 8
      }
    },
  }
}

// Bar Chart Component
interface BarChartProps {
  data: ChartData<'bar'>
  options?: ChartOptions<'bar'>
}

export function BarChart({ data, options = {} }: BarChartProps) {
  const barOptions: ChartOptions<'bar'> = {
    ...commonOptions,
    // Type-specific options can be added here
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    ...options
  }
  return <Bar data={data} options={barOptions} />
}

// Line Chart Component
interface LineChartProps {
  data: ChartData<'line'>
  options?: ChartOptions<'line'>
}

export function LineChart({ data, options = {} }: LineChartProps) {
  const lineOptions: ChartOptions<'line'> = {
    ...commonOptions,
    // Type-specific options can be added here
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    ...options
  }
  return <Line data={data} options={lineOptions} />
}

// Pie Chart Component
interface PieChartProps {
  data: ChartData<'pie'>
  options?: ChartOptions<'pie'>
}

export function PieChart({ data, options = {} }: PieChartProps) {
  const pieOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      ...commonOptions.plugins,
      legend: {
        position: isMobileScreen() ? 'bottom' : 'right' as const,
        labels: {
          font: {
            family: 'Inter, system-ui, sans-serif',
            size: isMobileScreen() ? 9 : 12
          },
          usePointStyle: true,
          boxWidth: isMobileScreen() ? 6 : 8
        }
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    ...options
  }
  return <Pie data={data} options={pieOptions} />
}

// Doughnut Chart Component
interface DoughnutChartProps {
  data: ChartData<'doughnut'>
  options?: ChartOptions<'doughnut'>
}

export function DoughnutChart({ data, options = {} }: DoughnutChartProps) {
  const doughnutOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      ...commonOptions.plugins,
      legend: {
        position: isMobileScreen() ? 'bottom' : 'right' as const,
        labels: {
          font: {
            family: 'Inter, system-ui, sans-serif',
            size: isMobileScreen() ? 9 : 12
          },
          usePointStyle: true,
          boxWidth: isMobileScreen() ? 6 : 8
        }
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    ...options
  }
  return <Doughnut data={data} options={doughnutOptions} />
}