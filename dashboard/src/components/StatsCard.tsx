import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: string;
  trendColor?: 'green' | 'red' | 'gray';
}

export default function StatsCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  trendColor = 'gray'
}: StatsCardProps) {
  const trendColors = {
    green: 'text-green-600',
    red: 'text-red-600',
    gray: 'text-gray-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {description && (
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          )}
          {trend && (
            <p className={`text-sm font-medium mt-1 ${trendColors[trendColor]}`}>
              {trend}
            </p>
          )}
        </div>
        <div className="ml-4">
          <div className="bg-blue-100 rounded-full p-3">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>
    </div>
  );
}
