'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Loader2, AlertCircle, TrendingUp, Building2, BarChart3 } from 'lucide-react'
import axios from 'axios'

interface Sector {
  id: number
  name: string
  url: string
  companies_count: number
  is_visited: number
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SectorsPage() {
  const { data: sectors, isLoading, error } = useQuery({
    queryKey: ['sectors'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/sectors/analysis`)
      return response.data as Sector[]
    },
  })

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
        <p className="text-red-800">Error loading sectors</p>
      </div>
    )
  }

  const visitedSectors = sectors?.filter(s => s.is_visited === 1) || []
  const unvisitedSectors = sectors?.filter(s => s.is_visited === 0) || []
  const totalCompanies = sectors?.reduce((sum, s) => sum + s.companies_count, 0) || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <BarChart3 className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Sector Analysis</h1>
            <p className="text-gray-600">View and analyze companies by industry sectors</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Sectors</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {sectors?.length || 0}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Visited Sectors</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {visitedSectors.length}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Building2 className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Companies</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {totalCompanies}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <Building2 className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Visited Sectors */}
      {visitedSectors.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Visited Sectors ({visitedSectors.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visitedSectors.map((sector) => (
              <div
                key={sector.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg mb-2">
                      {sector.name}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <div className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-medium">
                        Visited
                      </div>
                      {sector.companies_count > 0 && (
                        <div className="text-gray-600 text-sm">
                          {sector.companies_count} companies
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="bg-green-100 p-2 rounded-lg">
                    <Building2 className="w-5 h-5 text-green-600" />
                  </div>
                </div>
                {sector.url && (
                  <a
                    href={sector.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    View on Screener.in →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unvisited Sectors */}
      {unvisitedSectors.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Pending Sectors ({unvisitedSectors.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {unvisitedSectors.map((sector) => (
              <div
                key={sector.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg mb-2">
                      {sector.name}
                    </h3>
                    <div className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-medium inline-block">
                      Not Visited
                    </div>
                  </div>
                  <div className="bg-gray-100 p-2 rounded-lg">
                    <Building2 className="w-5 h-5 text-gray-600" />
                  </div>
                </div>
                {sector.url && (
                  <a
                    href={sector.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    View on Screener.in →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
