'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Plus, X } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Company {
  company_name: string;
  stock_price: string;
  percentage_change: string;
  market_cap: string;
  ratios: Array<{ ratio_name: string; ratio_value: string }>;
}

export default function ComparePage() {
  const [selectedCompanies, setSelectedCompanies] = useState<Company[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Company[]>([]);
  const router = useRouter();

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const addCompany = async (companyName: string) => {
    if (selectedCompanies.some(c => c.company_name === companyName)) {
      return;
    }

    try {
      const response = await fetch(`/api/companies/${encodeURIComponent(companyName)}`);
      const data = await response.json();
      setSelectedCompanies([...selectedCompanies, data]);
      setSearchQuery('');
      setSearchResults([]);
    } catch (error) {
      console.error('Error fetching company:', error);
    }
  };

  const removeCompany = (companyName: string) => {
    setSelectedCompanies(selectedCompanies.filter(c => c.company_name !== companyName));
  };

  const getComparisonData = () => {
    if (selectedCompanies.length === 0) return [];

    const metrics = ['Stock P/E', 'ROE', 'ROCE', 'Dividend Yield'];
    return metrics.map(metric => {
      const dataPoint: any = { metric };
      selectedCompanies.forEach(company => {
        const ratio = company.ratios.find(r => r.ratio_name === metric);
        if (ratio) {
          const value = parseFloat(ratio.ratio_value.replace(/[^0-9.-]/g, ''));
          dataPoint[company.company_name] = isNaN(value) ? 0 : value;
        }
      });
      return dataPoint;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => router.push('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Dashboard
        </button>

        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <h1 className="text-3xl font-bold mb-6">Compare Companies</h1>

          {/* Search */}
          <div className="relative mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search for companies to compare..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {searchResults.map((company) => (
                  <button
                    key={company.company_name}
                    onClick={() => addCompany(company.company_name)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b last:border-b-0 flex justify-between items-center"
                  >
                    <span className="font-medium">{company.company_name}</span>
                    <Plus className="h-4 w-4 text-gray-400" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Selected Companies */}
          {selectedCompanies.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {selectedCompanies.map((company) => (
                <div
                  key={company.company_name}
                  className="inline-flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
                >
                  <span className="mr-2">{company.company_name}</span>
                  <button
                    onClick={() => removeCompany(company.company_name)}
                    className="hover:bg-blue-200 rounded-full p-1"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedCompanies.length >= 2 ? (
          <>
            {/* Comparison Chart */}
            <div className="bg-white rounded-lg shadow p-8 mb-6">
              <h2 className="text-2xl font-bold mb-6">Key Metrics Comparison</h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={getComparisonData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {selectedCompanies.map((company, index) => {
                    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];
                    return (
                      <Bar
                        key={company.company_name}
                        dataKey={company.company_name}
                        fill={colors[index % colors.length]}
                      />
                    );
                  })}
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Detailed Comparison Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="p-6 border-b">
                <h2 className="text-2xl font-bold">Detailed Comparison</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Metric
                      </th>
                      {selectedCompanies.map((company) => (
                        <th
                          key={company.company_name}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                        >
                          {company.company_name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                      <td className="px-6 py-4 font-medium text-gray-900">Stock Price</td>
                      {selectedCompanies.map((company) => (
                        <td key={company.company_name} className="px-6 py-4 text-gray-700">
                          {company.stock_price}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-6 py-4 font-medium text-gray-900">Change %</td>
                      {selectedCompanies.map((company) => (
                        <td
                          key={company.company_name}
                          className={`px-6 py-4 font-medium ${
                            company.percentage_change.startsWith('-') ? 'text-red-600' : 'text-green-600'
                          }`}
                        >
                          {company.percentage_change}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-6 py-4 font-medium text-gray-900">Market Cap</td>
                      {selectedCompanies.map((company) => (
                        <td key={company.company_name} className="px-6 py-4 text-gray-700">
                          {company.market_cap}
                        </td>
                      ))}
                    </tr>
                    {selectedCompanies[0].ratios.map((ratio) => (
                      <tr key={ratio.ratio_name}>
                        <td className="px-6 py-4 font-medium text-gray-900">{ratio.ratio_name}</td>
                        {selectedCompanies.map((company) => {
                          const companyRatio = company.ratios.find(r => r.ratio_name === ratio.ratio_name);
                          return (
                            <td key={company.company_name} className="px-6 py-4 text-gray-700">
                              {companyRatio?.ratio_value || 'N/A'}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg">
              Select at least 2 companies to compare
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
