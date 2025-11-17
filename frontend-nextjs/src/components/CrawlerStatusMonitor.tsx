'use client'

import { useState, useEffect } from 'react'
import { Activity, Loader2, CheckCircle, AlertCircle } from 'lucide-react'

interface CrawlerStatus {
  total_companies: number
  pending_in_queue: number
  companies_in_queue: number
  currently_processing: number
  timestamp: string
}

export default function CrawlerStatusMonitor() {
  const [status, setStatus] = useState<CrawlerStatus | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'
    let ws: WebSocket | null = null
    let reconnectTimeout: NodeJS.Timeout

    const connect = () => {
      try {
        ws = new WebSocket(`${WS_URL}/ws/crawler-status`)

        ws.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          setError(null)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            setStatus(data)
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e)
          }
        }

        ws.onerror = (event) => {
          console.error('WebSocket error:', event)
          setError('Connection error')
          setIsConnected(false)
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          // Attempt to reconnect after 5 seconds
          reconnectTimeout = setTimeout(connect, 5000)
        }
      } catch (e) {
        console.error('Failed to connect WebSocket:', e)
        setError('Failed to connect')
        reconnectTimeout = setTimeout(connect, 5000)
      }
    }

    connect()

    return () => {
      if (ws) {
        ws.close()
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
    }
  }, [])

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
        <AlertCircle className="w-5 h-5 text-red-600" />
        <div>
          <p className="text-sm font-medium text-red-800">Crawler Status Monitor</p>
          <p className="text-xs text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  if (!isConnected) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center space-x-3">
        <Loader2 className="w-5 h-5 animate-spin text-yellow-600" />
        <div>
          <p className="text-sm font-medium text-yellow-800">Connecting to crawler...</p>
        </div>
      </div>
    )
  }

  if (!status) {
    return null
  }

  const isProcessing = status.currently_processing > 0

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-blue-600" />
          <h3 className="text-sm font-semibold text-gray-900">Real-time Crawler Status</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-xs text-gray-600">
            {isProcessing ? 'Processing' : 'Idle'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-xs text-gray-600">Total Companies</p>
          <p className="text-lg font-bold text-gray-900">{status.total_companies}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">In Queue</p>
          <p className="text-lg font-bold text-blue-600">{status.companies_in_queue}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Processing</p>
          <p className="text-lg font-bold text-green-600">{status.currently_processing}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Status</p>
          <div className="flex items-center space-x-1 mt-1">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-600">Live</span>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Last update: {new Date(status.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}
