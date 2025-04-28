import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, User, Phone, Mail, MapPin, ArrowUpDown, MoreHorizontal, Star } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Modal from '../components/ui/Modal';
import { useTheme } from '../context/ThemeContext';
import LeadDetailsModal from '../components/leads/LeadDetailsModal';
import apiService from '../services/api';

interface Lead {
  id: string;
  name: string;
  organization?: string;
  company?: string; // For compatibility with both backend and frontend naming
  email?: string;
  phone?: string;
  location?: string;
  status?: 'New' | 'Contacted' | 'Qualified' | 'Proposal' | 'Converted' | 'Lost';
  source: string;
  score?: number;
  scrape_date?: string;
  notes?: string;
  role?: string;
}

const LeadsPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalLeads, setTotalLeads] = useState(0);
  const [leadsPerPage, setLeadsPerPage] = useState(10);
  const [sourceFilter, setSourceFilter] = useState<string | null>(null);

  // Load leads from API
  useEffect(() => {
    const fetchLeads = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const offset = (currentPage - 1) * leadsPerPage;
        const params: any = { 
          limit: leadsPerPage, 
          offset 
        };
        
        if (sourceFilter) {
          params.source = sourceFilter;
        }
        
        const response = await apiService.leads.getAll(params);
        setLeads(response);
        
        // Get total count
        const countResponse = await apiService.leads.getCount(sourceFilter || undefined);
        if (sourceFilter) {
          setTotalLeads(countResponse.count);
        } else {
          setTotalLeads(countResponse.total);
        }
      } catch (err: any) {
        console.error('Failed to fetch leads:', err);
        setError('Failed to load leads. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchLeads();
  }, [currentPage, leadsPerPage, sourceFilter]);

  const getStatusColor = (status: string) => {
    const colors = {
      New: 'bg-blue-100 text-blue-800',
      Contacted: 'bg-yellow-100 text-yellow-800',
      Qualified: 'bg-purple-100 text-purple-800',
      Proposal: 'bg-orange-100 text-orange-800',
      Converted: 'bg-green-100 text-green-800',
      Lost: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const handleOpenDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setIsDetailsModalOpen(true);
  };

  // Calculate pagination
  const totalPages = Math.ceil(totalLeads / leadsPerPage);
  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  // Filter leads based on search term
  const filteredLeads = leads.filter((lead) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      lead.name?.toLowerCase().includes(searchLower) ||
      lead.organization?.toLowerCase().includes(searchLower) ||
      lead.company?.toLowerCase().includes(searchLower) ||
      lead.email?.toLowerCase().includes(searchLower) ||
      lead.phone?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Lead Management</h1>
        <Button leftIcon={<Plus size={16} />}>Add Lead</Button>
      </div>
      
      <Card>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-4 gap-4">
          <div className={`relative flex-1 w-full max-w-md ${isDark ? 'bg-gray-700' : 'bg-gray-100'} rounded-lg`}>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-500" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border-0 rounded-lg bg-transparent focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Search leads..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              leftIcon={<Filter size={16} />}
              onClick={() => setSourceFilter(sourceFilter ? null : 'business_list')}
            >
              {sourceFilter ? `Clear Filter (${sourceFilter})` : 'Filter'}
            </Button>
            <Button variant="outline">Export</Button>
          </div>
        </div>
        
        {error && (
          <div className="bg-red-100 text-red-800 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
              <p className="text-gray-500">Loading leads...</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className={isDark ? 'bg-gray-700' : 'bg-gray-50'}>
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <div className="flex items-center space-x-1">
                      <span>Name</span>
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <div className="flex items-center space-x-1">
                      <span>Company</span>
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Source</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <div className="flex items-center space-x-1">
                      <span>Score</span>
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredLeads.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      No leads found. Try adjusting your search or filters.
                    </td>
                  </tr>
                ) : (
                  filteredLeads.map((lead) => (
                    <tr 
                      key={lead.id} 
                      className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} cursor-pointer transition-colors`}
                      onClick={() => handleOpenDetails(lead)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-3">
                            <User size={16} />
                          </div>
                          <div>
                            <div className="font-medium">{lead.name}</div>
                            <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{lead.email || 'No email'}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{lead.organization || lead.company || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {lead.status ? (
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(lead.status)}`}>
                            {lead.status}
                          </span>
                        ) : (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                            New
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{lead.source}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {lead.score !== undefined ? (
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2.5 mr-2">
                              <div 
                                className={`h-2.5 rounded-full ${
                                  lead.score >= 70 ? 'bg-green-500' : 
                                  lead.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                                }`} 
                                style={{ width: `${lead.score}%` }}
                              ></div>
                            </div>
                            <span>{lead.score}</span>
                          </div>
                        ) : (
                          'N/A'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="rounded-full"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Action menu
                          }}
                        >
                          <MoreHorizontal size={16} />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing {isLoading ? '...' : `${Math.min((currentPage - 1) * leadsPerPage + 1, totalLeads)} to ${Math.min(currentPage * leadsPerPage, totalLeads)} of ${totalLeads}`} results
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              disabled={!canGoPrevious || isLoading}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            >
              Previous
            </Button>
            
            {/* Page numbers */}
            {Array.from({ length: Math.min(3, totalPages) }, (_, i) => {
              const pageNumber = currentPage <= 2 ? i + 1 : currentPage - 1 + i;
              if (pageNumber <= totalPages) {
                return (
                  <Button 
                    key={pageNumber}
                    variant="outline" 
                    size="sm" 
                    className={pageNumber === currentPage ? (isDark ? 'bg-gray-700' : 'bg-gray-100') : ''}
                    onClick={() => setCurrentPage(pageNumber)}
                  >
                    {pageNumber}
                  </Button>
                );
              }
              return null;
            })}
            
            <Button 
              variant="outline" 
              size="sm"
              disabled={!canGoNext || isLoading}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
      
      {selectedLead && (
        <LeadDetailsModal
          isOpen={isDetailsModalOpen}
          onClose={() => setIsDetailsModalOpen(false)}
          lead={selectedLead}
        />
      )}
    </div>
  );
};

export default LeadsPage;