import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { BarChart3, Home, GitCompare } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Finance Data Dashboard',
  description: 'Interactive dashboard for Indian stock market financial data',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link href="/" className="flex items-center px-2 text-gray-900 hover:text-blue-600 transition-colors">
                  <BarChart3 className="h-6 w-6 mr-2" />
                  <span className="font-semibold text-lg">Finance Dashboard</span>
                </Link>
              </div>
              <div className="flex items-center space-x-4">
                <Link
                  href="/"
                  className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 transition-colors"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Home
                </Link>
                <Link
                  href="/compare"
                  className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 transition-colors"
                >
                  <GitCompare className="h-4 w-4 mr-2" />
                  Compare
                </Link>
              </div>
            </div>
          </div>
        </nav>
        {children}
        <footer className="bg-gray-800 text-white mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Finance Data Dashboard</h3>
                <p className="text-gray-400 text-sm">
                  Interactive dashboard for analyzing Indian stock market companies.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">Features</h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li>Company Search</li>
                  <li>Financial Data Visualization</li>
                  <li>Company Comparison</li>
                  <li>Real-time Statistics</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">Data Source</h3>
                <p className="text-gray-400 text-sm">
                  Data crawled from screener.in using the Finance Data Crawler.
                </p>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-400">
              <p>&copy; 2024 Finance Data Dashboard. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
