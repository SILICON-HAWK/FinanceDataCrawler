'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, TrendingDown, Building2, DollarSign, Percent } from 'lucide-react';
import QuarterlyChart from '@/components/QuarterlyChart';
import { formatDate, getChangeColor } from '@/lib/utils';

interface CompanyData {
  id: number;
  company_name: string;
  url: string;
  stock_price: string;
  percentage_change: string;
  market_cap: string;
  about: string;
  created_at: string;
  updated_at: string;
  ratios: Array<{
    ratio_name: string;
    ratio_value: string;
  }>;
  financial_data: {
    quarters_data?: any;
    profit_loss_data?: any;
    balance_sheet_data?: any;
    cash_flows_data?: any;
    ratios_data?: any;
    shareholding_data?: any;
  };
}

export default function CompanyPage({ params }: { params: Promise<{ name: string }> }) {
  const resolvedParams = use(params);
  const [company, setCompany] = useState<CompanyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        const response = await fetch(`/api/companies/${encodeURIComponent(resolvedParams.name)}`);
        if (!response.ok) {
          throw new Error('Company not found');
        }
        const data = await response.json();
        setCompany(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load company data');
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
  }, [resolvedParams.name]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-red-600 text-lg mb-4">{error || 'Company not found'}</p>
        <button
          onClick={() => router.push('/')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  const isPositiveChange = !company.percentage_change.startsWith('-');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Dashboard
        </button>

        {/* Company Overview */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{company.company_name}</h1>
              <p className="text-sm text-gray-500">Last updated: {formatDate(company.updated_at)}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-900">{company.stock_price}</div>
              <div className={`flex items-center justify-end mt-1 ${getChangeColor(company.percentage_change)}`}>
                {isPositiveChange ? <TrendingUp className="h-5 w-5 mr-1" /> : <TrendingDown className="h-5 w-5 mr-1" />}
                <span className="text-lg font-semibold">{company.percentage_change}</span>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {company.ratios.slice(0, 9).map((ratio) => (
              <div key={ratio.ratio_name} className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">{ratio.ratio_name}</p>
                <p className="text-lg font-semibold text-gray-900">{ratio.ratio_value}</p>
              </div>
            ))}
          </div>

          {/* About */}
          {company.about && (
            <div className="border-t pt-6">
              <h2 className="text-lg font-semibold mb-3">About</h2>
              <p className="text-gray-700 leading-relaxed">{company.about}</p>
            </div>
          )}
        </div>

        {/* Financial Charts */}
        {company.financial_data.quarters_data && (
          <div className="mb-6">
            <QuarterlyChart data={company.financial_data.quarters_data} />
          </div>
        )}

        {/* Shareholding Pattern */}
        {company.financial_data.shareholding_data && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Shareholding Pattern</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Quarterly */}
              {company.financial_data.shareholding_data.Quarterly && (
                <div>
                  <h3 className="text-lg font-medium mb-3">Quarterly</h3>
                  <div className="space-y-2">
                    {Object.entries(company.financial_data.shareholding_data.Quarterly).map(([category, data]: [string, any]) => (
                      <div key={category} className="bg-gray-50 rounded p-3">
                        <p className="font-medium text-gray-900 mb-2">{category}</p>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          {Object.entries(data).slice(0, 4).map(([quarter, value]: [string, any]) => (
                            <div key={quarter}>
                              <span className="text-gray-600">{quarter}:</span>
                              <span className="ml-2 font-medium">{value}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Yearly */}
              {company.financial_data.shareholding_data.Yearly && (
                <div>
                  <h3 className="text-lg font-medium mb-3">Yearly</h3>
                  <div className="space-y-2">
                    {Object.entries(company.financial_data.shareholding_data.Yearly).map(([category, data]: [string, any]) => (
                      <div key={category} className="bg-gray-50 rounded p-3">
                        <p className="font-medium text-gray-900 mb-2">{category}</p>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          {Object.entries(data).slice(0, 4).map(([year, value]: [string, any]) => (
                            <div key={year}>
                              <span className="text-gray-600">{year}:</span>
                              <span className="ml-2 font-medium">{value}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Profit & Loss */}
        {company.financial_data.profit_loss_data && company.financial_data.profit_loss_data['Profit & Loss'] && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Profit & Loss Statement</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                    {Object.entries(company.financial_data.profit_loss_data['Profit & Loss']).slice(0, 5).map(([year]) => (
                      <th key={year} className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{year}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {['Sales', 'Expenses', 'Operating Profit', 'Net Profit'].map((metric) => (
                    <tr key={metric}>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{metric}</td>
                      {Object.entries(company.financial_data.profit_loss_data['Profit & Loss']).slice(0, 5).map(([year, data]: [string, any]) => (
                        <td key={year} className="px-4 py-3 text-sm text-gray-700 text-right">{data[metric] || 'N/A'}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Compounded Growth */}
        {company.financial_data.profit_loss_data && company.financial_data.profit_loss_data['Compounded Growth'] && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Compounded Growth Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(company.financial_data.profit_loss_data['Compounded Growth']).map(([metric, data]: [string, any]) => (
                <div key={metric} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">{metric}</h3>
                  <div className="space-y-2">
                    {Object.entries(data).map(([period, value]: [string, any]) => (
                      <div key={period} className="flex justify-between">
                        <span className="text-sm text-gray-600">{period}</span>
                        <span className="text-sm font-semibold text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
