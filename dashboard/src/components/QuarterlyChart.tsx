'use client';

import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface QuarterlyChartProps {
  data: any;
  type?: 'line' | 'bar';
}

export default function QuarterlyChart({ data, type = 'line' }: QuarterlyChartProps) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No quarterly data available</p>
      </div>
    );
  }

  // Transform data for charts
  const quarters = Object.keys(data);
  const chartData = quarters.map(quarter => {
    const quarterData = data[quarter];
    return {
      quarter,
      sales: parseFloat(quarterData.Sales?.replace(/,/g, '') || '0'),
      profit: parseFloat(quarterData['Net Profit']?.replace(/,/g, '') || '0'),
      opm: parseFloat(quarterData['OPM %']?.replace(/,/g, '') || '0'),
    };
  }).reverse(); // Reverse to show chronological order

  const Chart = type === 'line' ? LineChart : BarChart;
  const Element = type === 'line' ? Line : Bar;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Quarterly Performance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <Chart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="quarter" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Element yAxisId="left" type="monotone" dataKey="sales" stroke="#8884d8" fill="#8884d8" name="Sales (Cr)" />
          <Element yAxisId="left" type="monotone" dataKey="profit" stroke="#82ca9d" fill="#82ca9d" name="Net Profit (Cr)" />
          <Element yAxisId="right" type="monotone" dataKey="opm" stroke="#ffc658" fill="#ffc658" name="OPM %" />
        </Chart>
      </ResponsiveContainer>
    </div>
  );
}
