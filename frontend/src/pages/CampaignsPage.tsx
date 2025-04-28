import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Mail, Users, BarChart, Calendar } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const CampaignsPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const campaigns = [
    {
      name: 'Q1 Outreach',
      status: 'Active',
      sent: 1250,
      opened: 876,
      clicked: 234,
      converted: 45,
      lastSent: '2 hours ago'
    },
    {
      name: 'Product Launch',
      status: 'Scheduled',
      sent: 0,
      opened: 0,
      clicked: 0,
      converted: 0,
      lastSent: 'Starts in 2 days'
    },
    {
      name: 'Follow-up Sequence',
      status: 'Active',
      sent: 450,
      opened: 328,
      clicked: 156,
      converted: 28,
      lastSent: '5 hours ago'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Email Campaigns</h1>
        <Button leftIcon={<Mail size={16} />}>Create Campaign</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Active Campaigns
              </p>
              <h3 className="text-2xl font-bold mt-1">12</h3>
            </div>
            <div className="bg-blue-500 p-3 rounded-lg text-white">
              <Mail size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Total Recipients
              </p>
              <h3 className="text-2xl font-bold mt-1">4,827</h3>
            </div>
            <div className="bg-purple-500 p-3 rounded-lg text-white">
              <Users size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Avg. Open Rate
              </p>
              <h3 className="text-2xl font-bold mt-1">68.5%</h3>
            </div>
            <div className="bg-green-500 p-3 rounded-lg text-white">
              <BarChart size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Scheduled
              </p>
              <h3 className="text-2xl font-bold mt-1">5</h3>
            </div>
            <div className="bg-orange-500 p-3 rounded-lg text-white">
              <Calendar size={20} />
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className={isDark ? 'bg-gray-700' : 'bg-gray-50'}>
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Campaign Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Sent
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Opened
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Clicked
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Converted
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Last Sent
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {campaigns.map((campaign, index) => (
                <tr 
                  key={index}
                  className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} cursor-pointer transition-colors`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <Mail size={16} />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium">{campaign.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      campaign.status === 'Active' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {campaign.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {campaign.sent.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {campaign.opened.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {campaign.clicked.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {campaign.converted.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {campaign.lastSent}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default CampaignsPage;