'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { TrendingUp, BarChart3, GitCompare, Plus, Layers } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: BarChart3 },
  { path: '/sectors', label: 'Sectors', icon: Layers },
  { path: '/compare', label: 'Compare', icon: GitCompare },
  { path: '/add-company', label: 'Add Company', icon: Plus },
]

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Finance Data Crawler</h1>
              <p className="text-xs text-gray-500">Real-time Financial Analytics</p>
            </div>
          </Link>

          <nav className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.path
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
