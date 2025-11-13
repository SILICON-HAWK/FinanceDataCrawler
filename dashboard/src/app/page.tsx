'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Database, TrendingUp, AlertCircle, Clock, Search as SearchIcon } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import StatsCard from '@/components/StatsCard';
import { formatDate, getChangeColor } from '@/lib/utils';

interface Stats {
  totalCompanies: number;
  successfulCrawls: number;
  failedCrawls: number;
  recentCompanies: Array<{
    company_name: string;
    created_at: string;
  }>;
  topPerformers: Array<{
    company_name: string;
    stock_price: string;
    percentage_change: string;
    market_cap: string;
  }>;
}

interface Company {
  id: number;
  company_name: string;
  stock_price: string;
  percentage_change: string;
  market_cap: string;
}

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, companiesRes] = await Promise.all([
          fetch('/api/stats'),
          fetch('/api/companies')
        ]);

        const statsData = await statsRes.json();
        const companiesData = await companiesRes.json();

        setStats(statsData);
        setCompanies(companiesData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold mb-4">Finance Data Dashboard</h1>
          <p className="text-blue-100 text-lg mb-8">
            Interactive dashboard for Indian stock market financial data
          </p>
          <SearchBar />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Companies"
            value={stats?.totalCompanies || 0}
            icon={Database}
            description="Companies in database"
          />
          <StatsCard
            title="Successful Crawls"
            value={stats?.successfulCrawls || 0}
            icon={TrendingUp}
            description="Data successfully extracted"
            trendColor="green"
          />
          <StatsCard
            title="Failed Crawls"
            value={stats?.failedCrawls || 0}
            icon={AlertCircle}
            description="Errors encountered"
            trendColor={stats && stats.failedCrawls > 0 ? 'red' : 'gray'}
          />
          <StatsCard
            title="Recent Updates"
            value={stats?.recentCompanies.length || 0}
            icon={Clock}
            description="Companies updated recently"
          />
        </div>

        {/* Top Performers */}
        {stats && stats.topPerformers && stats.topPerformers.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Top Performers</h2>
              <p className="text-gray-600 mt-1">Companies with highest positive change</p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Change
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Cap
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.topPerformers.map((company) => (
                    <tr
                      key={company.company_name}
                      onClick={() => router.push(`/company/${encodeURIComponent(company.company_name)}`)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{company.company_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{company.stock_price}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${getChangeColor(company.percentage_change)}`}>
                          {company.percentage_change}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{company.market_cap}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* All Companies */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">All Companies</h2>
              <p className="text-gray-600 mt-1">{companies.length} companies available</p>
            </div>
            <div className="flex items-center text-gray-500">
              <SearchIcon className="h-5 w-5 mr-2" />
              <span className="text-sm">Click on any company to view details</span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stock Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Change %
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Cap
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {companies.map((company) => (
                  <tr
                    key={company.id}
                    onClick={() => router.push(`/company/${encodeURIComponent(company.company_name)}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{company.company_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{company.stock_price}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${getChangeColor(company.percentage_change)}`}>
                        {company.percentage_change}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{company.market_cap}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
