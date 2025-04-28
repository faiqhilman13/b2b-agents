import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { FileText, Plus, Clock, CheckCircle, XCircle, MoreHorizontal } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const ProposalsPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const proposals = [
    {
      id: 1,
      title: 'Enterprise Software Solution',
      client: 'Acme Corp',
      value: '$75,000',
      status: 'Pending',
      dueDate: '2024-03-25',
      lastModified: '2 hours ago'
    },
    {
      id: 2,
      title: 'Digital Transformation Project',
      client: 'Globex Industries',
      value: '$120,000',
      status: 'Approved',
      dueDate: '2024-03-30',
      lastModified: '1 day ago'
    },
    {
      id: 3,
      title: 'Cloud Migration Services',
      client: 'Tech Solutions Inc',
      value: '$95,000',
      status: 'Rejected',
      dueDate: '2024-03-20',
      lastModified: '3 days ago'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Proposals</h1>
        <Button leftIcon={<Plus size={16} />}>Create Proposal</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Active Proposals
              </p>
              <h3 className="text-2xl font-bold mt-1">12</h3>
            </div>
            <div className="bg-blue-500 p-3 rounded-lg text-white">
              <FileText size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Pending Review
              </p>
              <h3 className="text-2xl font-bold mt-1">5</h3>
            </div>
            <div className="bg-yellow-500 p-3 rounded-lg text-white">
              <Clock size={20} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                Approval Rate
              </p>
              <h3 className="text-2xl font-bold mt-1">68%</h3>
            </div>
            <div className="bg-green-500 p-3 rounded-lg text-white">
              <CheckCircle size={20} />
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
                  Proposal
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Client
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Value
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Due Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Last Modified
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {proposals.map((proposal) => (
                <tr 
                  key={proposal.id}
                  className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} cursor-pointer transition-colors`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <FileText size={16} />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium">{proposal.title}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {proposal.client}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {proposal.value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      proposal.status === 'Approved' 
                        ? 'bg-green-100 text-green-800'
                        : proposal.status === 'Pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {proposal.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {proposal.dueDate}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {proposal.lastModified}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="rounded-full"
                    >
                      <MoreHorizontal size={16} />
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

export default ProposalsPage;