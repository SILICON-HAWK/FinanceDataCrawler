import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Companies API
export const getCompanies = async () => {
  const response = await api.get('/api/companies')
  return response.data
}

export const getCompany = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}`)
  return response.data
}

export const getBalanceSheet = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/balance-sheet`)
  return response.data
}

export const getProfitLoss = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/profit-loss`)
  return response.data
}

export const getCashFlows = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/cash-flows`)
  return response.data
}

export const getQuarters = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/quarters`)
  return response.data
}

export const getRatios = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/ratios`)
  return response.data
}

export const getShareholding = async (companyName) => {
  const response = await api.get(`/api/companies/${encodeURIComponent(companyName)}/shareholding`)
  return response.data
}

// Search API
export const searchCompanies = async (query) => {
  const response = await api.post('/api/search', { query })
  return response.data
}

// Compare API
export const compareCompanies = async (companyNames) => {
  const response = await api.post('/api/companies/compare', companyNames)
  return response.data
}

// Queue API
export const getQueueStatus = async () => {
  const response = await api.get('/api/queue/status')
  return response.data
}

export const addCompanyToQueue = async (companyUrl) => {
  const response = await api.post('/api/crawl/add-company', {
    company_url: companyUrl,
  })
  return response.data
}

// Stats API
export const getStats = async () => {
  const response = await api.get('/api/stats')
  return response.data
}

// Latest financials
export const getLatestFinancials = async () => {
  const response = await api.get('/api/financials/latest')
  return response.data
}

export default api
