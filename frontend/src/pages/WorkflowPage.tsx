import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { GitBranch, Plus, Play, Pause, AlertCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const WorkflowPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const workflows = [
    {
      id: 1,
      name: 'Lead Nurturing Sequence',
      status: 'Active',
      type: 'Email',
      triggers: 'New Lead Created',
      lastRun: '5 minutes ago',
      stats: {
        completed: 245,
        active: 23,
        failed: 2
      }
    },
    {
      id: 2,
      name: 'Follow-up Reminder',
      status: 'Paused',
      type: 'Task',
      triggers: 'No Activity (7 days)',
      lastRun: '2 hours ago',
      stats: {
        completed: 156,
        active: 0,
        failed: 5
      }
    },
    {
      id: 3,
      name: 'Deal Stage Update',
      status: 'Active',
      type: 'Automation',
      triggers: 'Proposal Accepted',
      lastRun: '1 hour ago',
      stats: {
        completed: 89,
        active: 12,
        failed: 1
      }
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Workflow Automation</h1>
        <Button leftIcon={<Plus size={16} />}>Create Workflow</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Active Workflows
              </p>
              <h3 className="text-2xl font-bold mt-1">8</h3>
            </div>
            <div className="bg-green-500 p-3 rounded-lg text-white">
              <Play size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Paused
              </p>
              <h3 className="text-2xl font-bold mt-1">2</h3>
            </div>
            <div className="bg-yellow-500 p-3 rounded-lg text-white">
              <Pause size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Errors Today
              </p>
              <h3 className="text-2xl font-bold mt-1">3</h3>
            </div>
            <div className="bg-red-500 p-3 rounded-lg text-white">
              <AlertCircle size={20} />
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
                  Workflow
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Triggers
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Stats
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
              {workflows.map((workflow) => (
                <tr 
                  key={workflow.id}
                  className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} cursor-pointer transition-colors`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <GitBranch size={16} />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium">{workflow.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      workflow.status === 'Active' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {workflow.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {workflow.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {workflow.triggers}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-2 text-sm">
                      <span className="text-green-600">{workflow.stats.completed} completed</span>
                      <span className="text-blue-600">{workflow.stats.active} active</span>
                      <span className="text-red-600">{workflow.stats.failed} failed</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {workflow.lastRun}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Button 
                      variant="outline"
                      size="sm"
                    >
                      {workflow.status === 'Active' ? 'Pause' : 'Resume'}
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

export default WorkflowPage;