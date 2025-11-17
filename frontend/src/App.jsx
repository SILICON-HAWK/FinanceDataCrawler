import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CompanyDetail from './pages/CompanyDetail'
import CompanyComparison from './pages/CompanyComparison'
import AddCompany from './pages/AddCompany'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="company/:companyName" element={<CompanyDetail />} />
          <Route path="compare" element={<CompanyComparison />} />
          <Route path="add-company" element={<AddCompany />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
