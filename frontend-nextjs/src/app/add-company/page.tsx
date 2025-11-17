'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, CheckCircle, AlertCircle, Loader2, ExternalLink } from 'lucide-react'
import { addCompanyToQueue, getQueueStatus } from '@/lib/api'

export default function AddCompanyPage() {
  const [companyUrl, setCompanyUrl] = useState('')
  const [priority, setPriority] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const { data: queueStatus, refetch } = useQuery({
    queryKey: ['queueStatus'],
    queryFn: getQueueStatus,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!companyUrl.trim()) {
      setMessage({ type: 'error', text: 'Please enter a valid company URL' })
      return
    }

    // Validate URL format
    if (!companyUrl.includes('screener.in/company/')) {
      setMessage({
        type: 'error',
        text: 'Please enter a valid Screener.in company URL (e.g., https://www.screener.in/company/COMPANYNAME/)'
      })
      return
    }

    setIsSubmitting(true)
    setMessage(null)

    try {
      const result = await addCompanyToQueue(companyUrl, priority)
      setMessage({
        type: 'success',
        text: `Company added to crawl queue successfully! ${result.message}`
      })
      setCompanyUrl('')
      setPriority(0)
      refetch() // Refresh queue status
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Error adding company to queue'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-2">
          <Plus className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Add Company to Crawl Queue</h1>
            <p className="text-gray-600">Submit a company URL from Screener.in to be crawled</p>
          </div>
        </div>
      </div>

      {/* Queue Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">Current Queue Status</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-blue-700">Companies in Queue</p>
            <p className="text-2xl font-bold text-blue-900">{queueStatus?.companies_in_queue || 0}</p>
          </div>
          <div>
            <p className="text-sm text-blue-700">Total Scraped</p>
            <p className="text-2xl font-bold text-blue-900">{queueStatus?.total_companies_scraped || 0}</p>
          </div>
        </div>
      </div>

      {/* Add Company Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
        <div>
          <label htmlFor="companyUrl" className="block text-sm font-medium text-gray-700 mb-2">
            Company URL
          </label>
          <input
            type="text"
            id="companyUrl"
            value={companyUrl}
            onChange={(e) => setCompanyUrl(e.target.value)}
            placeholder="https://www.screener.in/company/COMPANYNAME/"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
          <p className="mt-2 text-sm text-gray-500">
            Example: https://www.screener.in/company/RELIANCE/
          </p>
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
            Priority (0-10)
          </label>
          <input
            type="number"
            id="priority"
            value={priority}
            onChange={(e) => setPriority(parseInt(e.target.value) || 0)}
            min="0"
            max="10"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
          <p className="mt-2 text-sm text-gray-500">
            Higher priority companies will be crawled first (0 = normal priority)
          </p>
        </div>

        {message && (
          <div
            className={`flex items-center space-x-3 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <p
              className={`text-sm ${
                message.type === 'success' ? 'text-green-800' : 'text-red-800'
              }`}
            >
              {message.text}
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Adding to Queue...</span>
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              <span>Add to Crawl Queue</span>
            </>
          )}
        </button>
      </form>

      {/* Instructions */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">How to Find Company URLs</h2>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li>
            Visit{' '}
            <a
              href="https://www.screener.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 inline-flex items-center"
            >
              Screener.in
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </li>
          <li>Search for the company you want to track</li>
          <li>Click on the company name to open its detail page</li>
          <li>Copy the URL from your browser's address bar</li>
          <li>Paste the URL in the form above and submit</li>
        </ol>
      </div>
    </div>
  )
}
