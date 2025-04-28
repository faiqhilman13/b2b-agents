import React, { ReactNode } from 'react';
import Card from '../ui/Card';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface MetricsCardProps {
  title: string;
  value: string;
  change?: string;
  isPositive?: boolean;
  icon?: ReactNode;
  color?: string;
}

const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  change,
  isPositive = true,
  icon,
  color = 'bg-blue-500'
}) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  return (
    <Card className="transition-transform duration-200 hover:scale-[1.02]">
      <div className="flex items-start justify-between">
        <div>
          <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            {title}
          </p>
          <h3 className="text-2xl font-bold mt-1">{value}</h3>
          
          {change && (
            <div className="flex items-center mt-2">
              {isPositive ? (
                <TrendingUp size={16} className="text-green-500 mr-1" />
              ) : (
                <TrendingDown size={16} className="text-red-500 mr-1" />
              )}
              <span className={`text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {change}
              </span>
            </div>
          )}
        </div>
        
        <div className={`${color} p-3 rounded-lg text-white`}>
          {icon}
        </div>
      </div>
    </Card>
  );
};

export default MetricsCard;