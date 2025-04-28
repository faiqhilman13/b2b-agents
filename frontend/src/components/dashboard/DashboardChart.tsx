import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface DashboardChartProps {
  type: 'line' | 'bar' | 'pie';
  label: string;
  isDark: boolean;
  data?: {
    labels?: string[];
    datasets?: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string;
      borderDash?: number[];
      tension?: number;
      fill?: boolean;
    }>;
  };
}

const DashboardChart: React.FC<DashboardChartProps> = ({ type, label, isDark, data }) => {
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstance = useRef<Chart | null>(null);
  
  const generateRandomData = (count: number, max: number, min: number = 0) => {
    return Array.from({ length: count }, () => Math.floor(Math.random() * (max - min) + min));
  };
  
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const recentMonths = months.slice(0, 6);
  
  const colors = {
    blue: 'rgba(0, 86, 214, 0.7)',
    blueLight: 'rgba(0, 86, 214, 0.3)',
    red: 'rgba(230, 57, 70, 0.7)',
    redLight: 'rgba(230, 57, 70, 0.3)',
    green: 'rgba(41, 155, 99, 0.7)',
    greenLight: 'rgba(41, 155, 99, 0.3)',
    purple: 'rgba(128, 0, 255, 0.7)',
    purpleLight: 'rgba(128, 0, 255, 0.3)',
    orange: 'rgba(255, 159, 28, 0.7)',
    orangeLight: 'rgba(255, 159, 28, 0.3)',
  };
  
  // Chart configurations based on type
  const getChartConfig = () => {
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: isDark ? '#E5E7EB' : '#374151',
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          backgroundColor: isDark ? '#374151' : '#FFFFFF',
          titleColor: isDark ? '#F3F4F6' : '#111827',
          bodyColor: isDark ? '#E5E7EB' : '#374151',
          borderColor: isDark ? '#4B5563' : '#E5E7EB',
          borderWidth: 1
        }
      },
      scales: type !== 'pie' ? {
        x: {
          grid: {
            color: isDark ? 'rgba(75, 85, 99, 0.3)' : 'rgba(229, 231, 235, 0.8)',
          },
          ticks: {
            color: isDark ? '#9CA3AF' : '#6B7280'
          }
        },
        y: {
          grid: {
            color: isDark ? 'rgba(75, 85, 99, 0.3)' : 'rgba(229, 231, 235, 0.8)',
          },
          ticks: {
            color: isDark ? '#9CA3AF' : '#6B7280'
          }
        }
      } : undefined
    };
    
    // Use provided data if available, otherwise use default mock data
    if (data) {
      return {
        type,
        data,
        options: defaultOptions
      };
    }
    
    // Default data configuration based on chart type
    const configs = {
      line: {
        type: 'line',
        data: {
          labels: months,
          datasets: [
            {
              label: 'This Year',
              data: generateRandomData(12, 100),
              borderColor: colors.blue,
              backgroundColor: colors.blueLight,
              tension: 0.4,
              fill: true
            },
            {
              label: 'Last Year',
              data: generateRandomData(12, 100),
              borderColor: colors.red,
              backgroundColor: 'transparent',
              tension: 0.4,
              borderDash: [5, 5]
            }
          ]
        },
        options: defaultOptions
      },
      
      bar: {
        type: 'bar',
        data: {
          labels: recentMonths,
          datasets: [
            {
              label: 'Direct',
              data: generateRandomData(6, 50),
              backgroundColor: colors.blue
            },
            {
              label: 'Referral',
              data: generateRandomData(6, 50),
              backgroundColor: colors.purple
            },
            {
              label: 'Social',
              data: generateRandomData(6, 50),
              backgroundColor: colors.green
            }
          ]
        },
        options: defaultOptions
      },
      
      pie: {
        type: 'pie',
        data: {
          labels: ['Website', 'Social Media', 'Email', 'Referral', 'Other'],
          datasets: [
            {
              data: generateRandomData(5, 100, 20),
              backgroundColor: [
                colors.blue,
                colors.purple,
                colors.green,
                colors.orange,
                colors.red
              ]
            }
          ]
        },
        options: defaultOptions
      }
    };
    
    return configs[type];
  };
  
  useEffect(() => {
    if (chartRef.current) {
      // Destroy existing chart if it exists
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      
      // Get the chart configuration
      const chartConfig = getChartConfig();
      
      // Create new chart
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        chartInstance.current = new Chart(ctx, chartConfig as any);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [type, isDark, data]);
  
  return (
    <canvas ref={chartRef} />
  );
};

export default DashboardChart;