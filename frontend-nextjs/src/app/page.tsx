'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Search } from 'lucide-react'
import { getCompanies, getQueueStatus, searchCompanies } from '@/lib/api'
import CrawlerStatusMonitor from '@/components/CrawlerStatusMonitor'

export default function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState<any[] | null>(null)
  const [isSearching, setIsSearching] = useState(false)

  const { data: companies, isLoading, error } = useQuery({
    queryKey: ['companies'],
    queryFn: getCompanies,
  })

  const { data: queueStatus } = useQuery({
    queryKey: ['queueStatus'],
    queryFn: getQueueStatus,
    refetchInterval: 30000,
  })

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (searchTerm.trim()) {
      setIsSearching(true)
      try {
        const results = await searchCompanies(searchTerm)
        setSearchResults(results)
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setIsSearching(false)
      }
    } else {
      setSearchResults(null)
    }
  }

  const displayCompanies = searchResults || companies || []

  const getPriceChangeSymbol = (change?: string) => {
    if (!change) return ''
    const value = parseFloat(change.replace('%', ''))
    return value >= 0 ? '+' : ''
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin"></div>
          <p className="text-sm text-gray-600">Loading companies...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="border border-gray-300 rounded p-4">
        <p className="text-sm text-gray-700">Error loading companies. Please ensure the backend is running.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Real-time Crawler Status */}
      <CrawlerStatusMonitor />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border border-gray-200 rounded p-6 bg-white">
          <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">Total Companies</p>
          <p className="text-3xl font-light text-gray-900">
            {queueStatus?.total_companies_scraped || companies?.length || 0}
          </p>
        </div>

        <div className="border border-gray-200 rounded p-6 bg-white">
          <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">In Queue</p>
          <p className="text-3xl font-light text-gray-900">
            {queueStatus?.companies_in_queue || 0}
          </p>
        </div>

        <div className="border border-gray-200 rounded p-6 bg-white">
          <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">Sectors</p>
          <p className="text-3xl font-light text-gray-900">
            {queueStatus?.sectors_in_queue || 0}
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="border border-gray-200 rounded p-6 bg-white">
        <form onSubmit={handleSearch} className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search companies..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded text-sm focus:outline-none focus:border-gray-900 transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="px-6 py-2.5 bg-gray-900 text-white rounded text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
          {searchResults && (
            <button
              type="button"
              onClick={() => {
                setSearchTerm('')
                setSearchResults(null)
              }}
              className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Companies List */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          {searchResults ? 'Search Results' : 'Companies'}
        </h2>
        {displayCompanies.length === 0 ? (
          <div className="border border-gray-200 rounded p-12 text-center bg-white">
            <p className="text-sm text-gray-500">
              {searchResults ? 'No companies found' : 'No companies available'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {displayCompanies.map((company: any) => (
              <Link
                key={company.id}
                href={`/company/${encodeURIComponent(company.name)}`}
                className="block border border-gray-200 rounded p-4 bg-white hover:border-gray-900 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">
                      {company.name}
                    </h3>
                    {company.market_cap && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        Market Cap: {company.market_cap}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center space-x-6 ml-4">
                    {company.stock_price && (
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          ₹{company.stock_price}
                        </p>
                        {company.percentage_change && (
                          <p className={`text-xs font-medium ${
                            parseFloat(company.percentage_change.replace('%', '')) >= 0
                              ? 'text-gray-900'
                              : 'text-gray-600'
                          }`}>
                            {getPriceChangeSymbol(company.percentage_change)}{company.percentage_change}
                          </p>
                        )}
                      </div>
                    )}
                    <div className="text-gray-400">→</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
