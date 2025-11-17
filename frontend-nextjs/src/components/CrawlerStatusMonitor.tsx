'use client'

import { useState, useEffect } from 'react'

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
      <div className="border border-gray-300 rounded p-3 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-wider text-gray-500">Backend Status</p>
            <p className="text-sm text-gray-900 mt-1">Connection Error</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-gray-400"></div>
        </div>
      </div>
    )
  }

  if (!isConnected) {
    return (
      <div className="border border-gray-300 rounded p-3 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-wider text-gray-500">Backend Status</p>
            <p className="text-sm text-gray-900 mt-1">Connecting...</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"></div>
        </div>
      </div>
    )
  }

  if (!status) {
    return null
  }

  const isProcessing = status.currently_processing > 0

  return (
    <div className="border border-gray-200 rounded p-4 bg-white">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-gray-500">Backend Status</p>
          <p className="text-sm font-medium text-gray-900 mt-1">
            {isProcessing ? 'Processing Data' : 'Online'}
          </p>
        </div>
        <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-gray-900 animate-pulse' : 'bg-gray-900'}`} />
      </div>

      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
        <div>
          <p className="text-xs text-gray-500">Total</p>
          <p className="text-lg font-light text-gray-900 mt-1">{status.total_companies}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Queue</p>
          <p className="text-lg font-light text-gray-900 mt-1">{status.companies_in_queue}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Active</p>
          <p className="text-lg font-light text-gray-900 mt-1">{status.currently_processing}</p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-400">
          Last update: {new Date(status.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}
