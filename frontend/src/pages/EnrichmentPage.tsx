import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Database, RefreshCw, CheckCircle, XCircle, Search } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const EnrichmentPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const enrichmentTasks = [
    {
      id: 1,
      name: 'Company Data Update',
      status: 'Completed',
      source: 'Clearbit',
      records: 156,
      matches: 142,
      lastRun: '1 hour ago'
    },
    {
      id: 2,
      name: 'Email Verification',
      status: 'In Progress',
      source: 'Hunter.io',
      records: 250,
      matches: 180,
      lastRun: 'Running...'
    },
    {
      id: 3,
      name: 'Social Media Profiles',
      status: 'Failed',
      source: 'LinkedIn',
      records: 89,
      matches: 0,
      lastRun: '2 hours ago'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Data Enrichment</h1>
        <Button leftIcon={<RefreshCw size={16} />}>Start Enrichment</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Processed Today
              </p>
              <h3 className="text-2xl font-bold mt-1">1,247</h3>
            </div>
            <div className="bg-blue-500 p-3 rounded-lg text-white">
              <Database size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Match Rate
              </p>
              <h3 className="text-2xl font-bold mt-1">86%</h3>
            </div>
            <div className="bg-green-500 p-3 rounded-lg text-white">
              <CheckCircle size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Failed
              </p>
              <h3 className="text-2xl font-bold mt-1">23</h3>
            </div>
            <div className="bg-red-500 p-3 rounded-lg text-white">
              <XCircle size={20} />
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="mb-4">
          <div className={`relative flex items-center ${isDark ? 'bg-gray-700' : 'bg-gray-100'} rounded-lg px-4 py-2`}>
            <Search size={20} className="text-gray-500 mr-3" />
            <input
              type="text"
              placeholder="Search enrichment tasks..."
              className={`block w-full bg-transparent border-0 focus:ring-0 outline-none ${
                isDark ? 'placeholder-gray-400' : 'placeholder-gray-500'
              }`}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className={isDark ? 'bg-gray-700' : 'bg-gray-50'}>
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Task Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Source
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Records
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Matches
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Last Run
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {enrichmentTasks.map((task) => (
                <tr 
                  key={task.id}
                  className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} cursor-pointer transition-colors`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <Database size={16} />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium">{task.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      task.status === 'Completed' 
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'In Progress'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {task.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {task.source}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {task.records}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {task.matches}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {task.lastRun}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Button 
                      variant="outline"
                      size="sm"
                      leftIcon={<RefreshCw size={14} />}
                    >
                      Retry
                    </Button>
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

export default EnrichmentPage;