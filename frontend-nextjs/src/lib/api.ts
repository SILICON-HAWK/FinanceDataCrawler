import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Company {
  id: number
  name: string
  stock_price?: string
  percentage_change?: string
  market_cap?: string
  current_price?: string
  stock_pe?: string
  book_value?: string
  dividend_yield?: string
  roce?: string
  roe?: string
  about?: string
}

export interface BalanceSheet {
  period: string
  equity_capital?: number
  reserves?: number
  borrowings?: number
  total_liabilities?: number
  fixed_assets?: number
  investments?: number
  total_assets?: number
}

export interface ProfitLoss {
  period: string
  sales?: number
  expenses?: number
  operating_profit?: number
  opm_percent?: number
  net_profit?: number
  eps?: number
}

export interface QueueStatus {
  companies_in_queue: number
  sectors_in_queue: number
  total_companies_scraped: number
}

// API Functions
export const getCompanies = async (): Promise<Company[]> => {
  const response = await api.get('/api/companies')
  return response.data
}

export const getCompany = async (companyName: string): Promise<Company> => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}`)
  return response.data
}

export const getBalanceSheet = async (companyName: string): Promise<BalanceSheet[]> => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/balance-sheet`)
  return response.data
}

export const getProfitLoss = async (companyName: string): Promise<ProfitLoss[]> => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/profit-loss`)
  return response.data
}

export const getCashFlows = async (companyName: string) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/cash-flows`)
  return response.data
}

export const getQuarters = async (companyName: string) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/quarters`)
  return response.data
}

export const getRatios = async (companyName: string) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/ratios`)
  return response.data
}

export const getShareholding = async (companyName: string) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/shareholding`)
  return response.data
}

export const searchCompanies = async (query: string): Promise<Company[]> => {
  const response = await api.post('/api/search', { query })
  return response.data
}

export const compareCompanies = async (companyNames: string[]) => {
  const response = await api.post('/api/companies/compare', companyNames)
  return response.data
}

export const getQueueStatus = async (): Promise<QueueStatus> => {
  const response = await api.get('/api/queue/status')
  return response.data
}

export const addCompanyToQueue = async (companyUrl: string, priority: number = 0) => {
  const response = await api.post('/api/crawl/add-company', {
    company_url: companyUrl,
    priority,
  })
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/api/stats')
  return response.data
}

export default api
