'use client'

import { use } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeft, Building2, TrendingUp, TrendingDown, Loader2, AlertCircle } from 'lucide-react'
import { getCompany, getBalanceSheet, getProfitLoss, getQuarters } from '@/lib/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function CompanyDetailPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = use(params)
  const companyName = decodeURIComponent(name)

  const { data: company, isLoading: companyLoading } = useQuery({
    queryKey: ['company', companyName],
    queryFn: () => getCompany(companyName),
  })

  const { data: balanceSheet } = useQuery({
    queryKey: ['balanceSheet', companyName],
    queryFn: () => getBalanceSheet(companyName),
    enabled: !!company,
  })

  const { data: profitLoss } = useQuery({
    queryKey: ['profitLoss', companyName],
    queryFn: () => getProfitLoss(companyName),
    enabled: !!company,
  })

  const { data: quarters } = useQuery({
    queryKey: ['quarters', companyName],
    queryFn: () => getQuarters(companyName),
    enabled: !!company,
  })

  if (companyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!company) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
        <AlertCircle className="w-5 h-5 text-red-600" />
        <p className="text-red-800">Company not found</p>
      </div>
    )
  }

  // Prepare chart data
  const plChartData = profitLoss?.slice().reverse().map(item => ({
    period: item.period,
    sales: item.sales ? Number(item.sales) : 0,
    netProfit: item.net_profit ? Number(item.net_profit) : 0,
  })) || []

  const bsChartData = balanceSheet?.slice().reverse().map(item => ({
    period: item.period,
    assets: item.total_assets ? Number(item.total_assets) : 0,
    liabilities: item.total_liabilities ? Number(item.total_liabilities) : 0,
  })) || []

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link
        href="/"
        className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>

      {/* Company Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Building2 className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
                {company.market_cap && (
                  <p className="text-gray-500 mt-1">Market Cap: {company.market_cap}</p>
                )}
              </div>
            </div>
          </div>
          {company.stock_price && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Stock Price</p>
              <p className="text-3xl font-bold text-gray-900">{company.stock_price}</p>
              {company.percentage_change && (
                <div className={`flex items-center justify-end space-x-1 mt-1 ${
                  parseFloat(company.percentage_change.replace('%', '')) >= 0
                    ? 'text-green-600'
                    : 'text-red-600'
                }`}>
                  {parseFloat(company.percentage_change.replace('%', '')) >= 0 ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <TrendingDown className="w-4 h-4" />
                  )}
                  <span className="font-semibold">{company.percentage_change}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {company.stock_pe && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">P/E Ratio</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{company.stock_pe}</p>
          </div>
        )}
        {company.book_value && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">Book Value</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{company.book_value}</p>
          </div>
        )}
        {company.roe && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">ROE</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{company.roe}</p>
          </div>
        )}
        {company.roce && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">ROCE</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{company.roce}</p>
          </div>
        )}
      </div>

      {/* About */}
      {company.about && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">About</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{company.about}</p>
        </div>
      )}

      {/* Profit & Loss Chart */}
      {plChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sales & Net Profit Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={plChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(value: number) => value.toFixed(2)} />
              <Legend />
              <Line type="monotone" dataKey="sales" stroke="#3b82f6" name="Sales" strokeWidth={2} />
              <Line type="monotone" dataKey="netProfit" stroke="#10b981" name="Net Profit" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Balance Sheet Chart */}
      {bsChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Assets vs Liabilities</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bsChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(value: number) => value.toFixed(2)} />
              <Legend />
              <Bar dataKey="assets" fill="#3b82f6" name="Total Assets" />
              <Bar dataKey="liabilities" fill="#ef4444" name="Total Liabilities" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Financial Data Tables */}
      {profitLoss && profitLoss.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Profit & Loss Statement</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sales</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Expenses</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Operating Profit</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net Profit</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">EPS</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {profitLoss.slice(0, 5).map((item, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.period}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{item.sales?.toFixed(2) || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{item.expenses?.toFixed(2) || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{item.operating_profit?.toFixed(2) || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{item.net_profit?.toFixed(2) || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{item.eps?.toFixed(2) || '-'}</td>
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
