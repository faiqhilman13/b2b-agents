import React, { useState, useEffect } from 'react';
import { BarChart, PieChart, TrendingUp, Users, Mail, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useTheme } from '../context/ThemeContext';
import DashboardChart from '../components/dashboard/DashboardChart';
import MetricsCard from '../components/dashboard/MetricsCard';
import apiService from '../services/api';

// Define interfaces for dashboard statistics
interface DashboardStats {
  date: string;
  emails_sent: number;
  emails_opened: number;
  responses_received: number;
  meetings_booked: number;
  leads_by_status: Record<string, number>;
  recent_generations: Array<{
    id: number;
    lead_id: number;
    template_name: string;
    subject: string;
    generated_at: string;
    sent_at: string | null;
  }>;
  available_templates: string[];
}

const Dashboard: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  // Add state for dashboard data, loading state, and error
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch dashboard statistics when component mounts
  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        setLoading(true);
        const response = await apiService.dashboard.getStatistics();
        setStats(response);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard statistics:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardStats();
  }, []);
  
  // Calculate metrics based on stats data
  const getMetrics = () => {
    if (!stats) {
      return [
        { 
          title: 'Total Leads', 
          value: '0', 
          change: 'Loading...', 
          isPositive: true,
          icon: <Users size={20} />,
          color: 'bg-blue-500'
        },
        { 
          title: 'Emails Sent', 
          value: '0', 
          change: 'Loading...', 
          isPositive: true,
          icon: <Mail size={20} />,
          color: 'bg-purple-500'
        },
        { 
          title: 'Responses', 
          value: '0', 
          change: 'Loading...', 
          isPositive: true,
          icon: <FileText size={20} />,
          color: 'bg-green-500'
        },
        { 
          title: 'Conversion Rate', 
          value: '0%', 
          change: 'Loading...', 
          isPositive: true,
          icon: <CheckCircle size={20} />,
          color: 'bg-orange-500'
        },
      ];
    }
    
    // Calculate total leads
    const totalLeads = Object.values(stats.leads_by_status).reduce((sum, count) => sum + count, 0);
    
    // Calculate conversion rate
    const booked = stats.leads_by_status['booked'] || 0;
    const closed = stats.leads_by_status['closed'] || 0;
    const conversionRate = totalLeads > 0 ? ((booked + closed) / totalLeads * 100).toFixed(1) : '0.0';
    
    return [
      { 
        title: 'Total Leads', 
        value: totalLeads.toString(), 
        change: `${stats.leads_by_status['new'] || 0} new`, 
        isPositive: true,
        icon: <Users size={20} />,
        color: 'bg-blue-500'
      },
      { 
        title: 'Emails Sent', 
        value: stats.emails_sent.toString(), 
        change: `${stats.emails_opened} opened`, 
        isPositive: true,
        icon: <Mail size={20} />,
        color: 'bg-purple-500'
      },
      { 
        title: 'Responses', 
        value: stats.responses_received.toString(), 
        change: `${stats.meetings_booked} meetings`, 
        isPositive: true,
        icon: <FileText size={20} />,
        color: 'bg-green-500'
      },
      { 
        title: 'Conversion Rate', 
        value: `${conversionRate}%`, 
        change: `${booked + closed} converted`,
        isPositive: true,
        icon: <CheckCircle size={20} />,
        color: 'bg-orange-500'
      },
    ];
  };
  
  // Generate chart data for lead sources
  const getLeadSourcesChartData = () => {
    if (!stats) return undefined;
    
    // Extract lead sources from the data
    // This assumes leads_by_status has data by source type
    const sourceTypes = ['google_maps', 'instagram', 'web_browser', 'manual', 'imported', 'other'];
    const sourceLabels = ['Google Maps', 'Instagram', 'Web Browser', 'Manual', 'Imported', 'Other'];
    
    // Get counts for each source (assuming they exist in the stats data)
    // If the actual data structure is different, this would need to be adjusted
    const sourceCounts = sourceTypes.map(type => {
      return stats.leads_by_status[type] || 0;
    });
    
    return {
      labels: sourceLabels,
      datasets: [
        {
          label: 'Lead Sources',
          data: sourceCounts,
          backgroundColor: [
            'rgba(0, 86, 214, 0.7)',
            'rgba(128, 0, 255, 0.7)',
            'rgba(41, 155, 99, 0.7)',
            'rgba(255, 159, 28, 0.7)',
            'rgba(230, 57, 70, 0.7)',
            'rgba(100, 100, 100, 0.7)'
          ]
        }
      ]
    };
  };
  
  // Generate chart data for lead acquisition over time
  const getLeadAcquisitionChartData = () => {
    if (!stats) return undefined;
    
    // For demonstration, we'll create synthetic monthly data
    // In a real implementation, you would get this from the API
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    
    // These would come from the API in a real implementation
    const sourcesData = {
      'Google Maps': [15, 25, 30, 35, 40, 45],
      'Instagram': [5, 10, 15, 20, 25, 30],
      'Web Browser': [10, 15, 20, 25, 30, 35]
    };
    
    return {
      labels: months,
      datasets: [
        {
          label: 'Google Maps',
          data: sourcesData['Google Maps'],
          backgroundColor: 'rgba(0, 86, 214, 0.7)'
        },
        {
          label: 'Instagram',
          data: sourcesData['Instagram'],
          backgroundColor: 'rgba(128, 0, 255, 0.7)'
        },
        {
          label: 'Web Browser',
          data: sourcesData['Web Browser'],
          backgroundColor: 'rgba(41, 155, 99, 0.7)'
        }
      ]
    };
  };
  
  // Generate chart data for lead status distribution
  const getLeadStatusChartData = () => {
    if (!stats) return undefined;
    
    // Get the status labels and counts
    const statusLabels = Object.keys(stats.leads_by_status)
      .filter(key => !['google_maps', 'instagram', 'web_browser', 'manual', 'imported', 'other'].includes(key))
      .map(status => status.charAt(0).toUpperCase() + status.slice(1)); // Capitalize
    
    const statusCounts = Object.entries(stats.leads_by_status)
      .filter(([key]) => !['google_maps', 'instagram', 'web_browser', 'manual', 'imported', 'other'].includes(key))
      .map(([_, count]) => count);
    
    return {
      labels: statusLabels,
      datasets: [
        {
          label: 'Leads by Status',
          data: statusCounts,
          backgroundColor: 'rgba(0, 86, 214, 0.2)',
          borderColor: 'rgba(0, 86, 214, 0.7)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">Export</Button>
          <Button size="sm">Add Lead</Button>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <div className="flex items-center space-x-3 text-red-600 dark:text-red-400">
            <AlertCircle size={20} />
            <p>{error}</p>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </Card>
      )}

      {/* Dashboard content */}
      {!loading && !error && stats && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {getMetrics().map((metric, index) => (
              <MetricsCard key={index} {...metric} />
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card 
              title="Lead Acquisition" 
              className="lg:col-span-2"
              subtitle="Last 30 days"
            >
              <div className="h-72 w-full">
                <DashboardChart 
                  type="bar"
                  label="Lead Acquisition"
                  isDark={isDark}
                  data={getLeadAcquisitionChartData()}
                />
              </div>
            </Card>

            <Card title="Lead Sources" subtitle="Distribution">
              <div className="h-64 w-full">
                <DashboardChart 
                  type="pie"
                  label="Lead Sources"
                  isDark={isDark}
                  data={getLeadSourcesChartData()}
                />
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card 
              title="Lead Status Distribution" 
              subtitle="Current status breakdown"
            >
              <div className="h-72 w-full">
                <DashboardChart 
                  type="line"
                  label="Status"
                  isDark={isDark}
                  data={getLeadStatusChartData()}
                />
              </div>
            </Card>
            
            <Card title="Recent Email Activities">
              <div className="space-y-4">
                {stats.recent_generations.map((generation) => (
                  <div 
                    key={generation.id} 
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      isDark ? 'bg-gray-750 hover:bg-gray-700' : 'bg-gray-50 hover:bg-gray-100'
                    } transition-colors cursor-pointer`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`h-10 w-10 rounded-full flex items-center justify-center ${generation.sent_at ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'}`}>
                        {generation.sent_at ? (
                          <CheckCircle size={18} />
                        ) : (
                          <Mail size={18} />
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{generation.subject}</div>
                        <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          {generation.sent_at ? 'Sent' : 'Generated'} - Lead #{generation.lead_id}
                        </div>
                      </div>
                    </div>
                    <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {new Date(generation.generated_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
                <Button variant="ghost" fullWidth>View All Activity</Button>
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;