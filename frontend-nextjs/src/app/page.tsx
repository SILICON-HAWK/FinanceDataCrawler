'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Search, Building2, TrendingUp, TrendingDown, Loader2, AlertCircle } from 'lucide-react'
import { getCompanies, getQueueStatus, searchCompanies } from '@/lib/api'

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

  const getPriceChangeColor = (change?: string) => {
    if (!change) return 'text-gray-500'
    const value = parseFloat(change.replace('%', ''))
    return value >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const getPriceChangeIcon = (change?: string) => {
    if (!change) return null
    const value = parseFloat(change.replace('%', ''))
    return value >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
        <AlertCircle className="w-5 h-5 text-red-600" />
        <p className="text-red-800">Error loading companies. Make sure the backend is running.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Companies</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {queueStatus?.total_companies_scraped || companies?.length || 0}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Companies in Queue</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {queueStatus?.companies_in_queue || 0}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Loader2 className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sectors in Queue</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {queueStatus?.sectors_in_queue || 0}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search companies..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
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
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Companies Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {searchResults ? 'Search Results' : 'All Companies'}
        </h2>
        {displayCompanies.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchResults ? 'No companies found' : 'No companies available. Add companies using the crawler or Add Company page.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayCompanies.map((company: any) => (
              <Link
                key={company.id}
                href={`/company/${encodeURIComponent(company.name)}`}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg mb-1">
                      {company.name}
                    </h3>
                    {company.market_cap && (
                      <p className="text-sm text-gray-500">
                        Market Cap: {company.market_cap}
                      </p>
                    )}
                  </div>
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <Building2 className="w-5 h-5 text-blue-600" />
                  </div>
                </div>

                {company.stock_price && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Stock Price</span>
                      <span className="text-lg font-bold text-gray-900">
                        {company.stock_price}
                      </span>
                    </div>
                    {company.percentage_change && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Change</span>
                        <span
                          className={`flex items-center space-x-1 font-semibold ${getPriceChangeColor(
                            company.percentage_change
                          )}`}
                        >
                          {getPriceChangeIcon(company.percentage_change)}
                          <span>{company.percentage_change}</span>
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
