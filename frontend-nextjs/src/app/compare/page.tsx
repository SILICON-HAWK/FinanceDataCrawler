'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { GitCompare, X, Plus, Loader2 } from 'lucide-react'
import { getCompanies, compareCompanies } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ComparisonPage() {
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  const [comparisonData, setComparisonData] = useState<any[] | null>(null)
  const [isComparing, setIsComparing] = useState(false)

  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: getCompanies,
  })

  const handleAddCompany = (companyName: string) => {
    if (!selectedCompanies.includes(companyName) && selectedCompanies.length < 5) {
      setSelectedCompanies([...selectedCompanies, companyName])
    }
  }

  const handleRemoveCompany = (companyName: string) => {
    setSelectedCompanies(selectedCompanies.filter(name => name !== companyName))
  }

  const handleCompare = async () => {
    if (selectedCompanies.length < 2) {
      alert('Please select at least 2 companies to compare')
      return
    }

    setIsComparing(true)
    try {
      const data = await compareCompanies(selectedCompanies)
      setComparisonData(data)
    } catch (error) {
      console.error('Comparison error:', error)
      alert('Error comparing companies')
    } finally {
      setIsComparing(false)
    }
  }

  // Prepare chart data
  const chartData = comparisonData?.map(item => ({
    name: item.company.name.substring(0, 20),
    marketCap: parseFloat(item.company.market_cap?.replace(/[^0-9.]/g, '') || '0'),
    stockPE: parseFloat(item.company.stock_pe || '0'),
    roe: parseFloat(item.company.roe?.replace('%', '') || '0'),
    roce: parseFloat(item.company.roce?.replace('%', '') || '0'),
  })) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <GitCompare className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Compare Companies</h1>
            <p className="text-gray-600">Select companies to compare their financials</p>
          </div>
        </div>

        {/* Selected Companies */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">
            Selected Companies ({selectedCompanies.length}/5):
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedCompanies.map(name => (
              <div
                key={name}
                className="flex items-center space-x-2 bg-blue-100 text-blue-700 px-3 py-2 rounded-lg"
              >
                <span className="font-medium">{name}</span>
                <button
                  onClick={() => handleRemoveCompany(name)}
                  className="hover:bg-blue-200 rounded-full p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Compare Button */}
        <button
          onClick={handleCompare}
          disabled={selectedCompanies.length < 2 || isComparing}
          className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isComparing ? (
            <span className="flex items-center justify-center space-x-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Comparing...</span>
            </span>
          ) : (
            'Compare Selected Companies'
          )}
        </button>
      </div>

      {/* Company Selection Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Select Companies</h2>
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {companies?.map(company => {
              const isSelected = selectedCompanies.includes(company.name)
              const canAdd = selectedCompanies.length < 5

              return (
                <button
                  key={company.id}
                  onClick={() => !isSelected && canAdd && handleAddCompany(company.name)}
                  disabled={isSelected || !canAdd}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    isSelected
                      ? 'border-blue-600 bg-blue-50'
                      : canAdd
                      ? 'border-gray-200 hover:border-blue-300 bg-white'
                      : 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{company.name}</h3>
                      {company.market_cap && (
                        <p className="text-sm text-gray-500 mt-1">
                          Market Cap: {company.market_cap}
                        </p>
                      )}
                    </div>
                    {isSelected ? (
                      <div className="bg-blue-600 text-white p-1 rounded-full">
                        <Plus className="w-4 h-4 transform rotate-45" />
                      </div>
                    ) : canAdd ? (
                      <div className="bg-gray-200 text-gray-600 p-1 rounded-full">
                        <Plus className="w-4 h-4" />
                      </div>
                    ) : null}
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparisonData && (
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Comparison Results</h2>

          {/* Key Metrics Comparison */}
          {chartData.length > 0 && (
            <>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">ROE & ROCE Comparison</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="roe" fill="#3b82f6" name="ROE %" />
                    <Bar dataKey="roce" fill="#10b981" name="ROCE %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">P/E Ratio Comparison</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="stockPE" fill="#8b5cf6" name="P/E Ratio" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}

          {/* Detailed Comparison Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 overflow-x-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Metrics</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Market Cap</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">P/E</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">ROE</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">ROCE</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Book Value</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {comparisonData.map((item, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.company.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {item.company.market_cap || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {item.company.stock_pe || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {item.company.roe || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {item.company.roce || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {item.company.book_value || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
