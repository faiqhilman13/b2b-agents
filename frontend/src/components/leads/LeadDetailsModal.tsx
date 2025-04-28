import React, { useState } from 'react';
import { Phone, Mail, MapPin, Building, Globe, Star, PenSquare, Calendar, Verified, History, BarChart, X, User } from 'lucide-react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import Card from '../ui/Card';
import { useTheme } from '../../context/ThemeContext';

interface Lead {
  id: string;
  name: string;
  organization?: string;
  company?: string;
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

interface LeadDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead: Lead;
}

const LeadDetailsModal: React.FC<LeadDetailsModalProps> = ({ isOpen, onClose, lead }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [activeTab, setActiveTab] = useState('overview');
  
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'activity', label: 'Activity' },
    { id: 'engagements', label: 'Engagements' },
    { id: 'documents', label: 'Documents' },
  ];
  
  // Mock timeline data
  const timelineData = [
    { date: '2 hours ago', event: 'Email opened', description: 'Lead opened the follow-up email', icon: Mail },
    { date: 'Yesterday', event: 'Note added', description: 'Call scheduled for next Tuesday', icon: PenSquare },
    { date: '3 days ago', event: 'Email sent', description: 'Follow-up email sent after initial contact', icon: Mail },
    { date: '5 days ago', event: 'Added to campaign', description: 'Added to "Q1 Outreach" campaign', icon: Globe },
    { date: '2 weeks ago', event: 'Lead created', description: 'Lead generated from website form', icon: Star },
  ];
  
  // Render based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <Card>
                <div className="flex flex-col items-center text-center">
                  <div className="h-20 w-20 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-3">
                    <Building size={32} />
                  </div>
                  <h3 className="text-lg font-bold">{lead.organization || lead.company || 'Not Available'}</h3>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    {lead.role || 'Unknown Role'}
                  </p>
                  
                  <div className="border-t border-b w-full my-4 py-4 grid grid-cols-2 gap-2">
                    <div className="text-center">
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Lead Score
                      </p>
                      <p className="text-lg font-bold">{lead.score ? `${lead.score}/100` : 'N/A'}</p>
                    </div>
                    <div className="text-center">
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Status
                      </p>
                      <p className="text-lg font-bold">{lead.status || 'New'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 mt-2 mb-4">
                    <div className={`p-1 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <Mail size={18} />
                    </div>
                    <div className={`p-1 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <Phone size={18} />
                    </div>
                    <div className={`p-1 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <Globe size={18} />
                    </div>
                  </div>
                </div>
              </Card>
              
              <Card className="mt-4">
                <h4 className="font-medium mb-3">Contact Details</h4>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} mr-3`}>
                      <User size={18} />
                    </div>
                    <div>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Full Name
                      </p>
                      <p className="font-medium">{lead.name}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} mr-3`}>
                      <Mail size={18} />
                    </div>
                    <div>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Email
                      </p>
                      <p className="font-medium">{lead.email || 'Not available'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} mr-3`}>
                      <Phone size={18} />
                    </div>
                    <div>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Phone
                      </p>
                      <p className="font-medium">{lead.phone || 'Not available'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} mr-3`}>
                      <MapPin size={18} />
                    </div>
                    <div>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Location
                      </p>
                      <p className="font-medium">{lead.location || 'Not available'}</p>
                    </div>
                  </div>
                  
                  {lead.scrape_date && (
                    <div className="flex items-start">
                      <div className={`p-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} mr-3`}>
                        <Calendar size={18} />
                      </div>
                      <div>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          Date Added
                        </p>
                        <p className="font-medium">{lead.scrape_date}</p>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </div>
            
            <div className="md:col-span-2">
              <Card>
                <h4 className="font-medium mb-3">Lead Activity Timeline</h4>
                <div className="space-y-4">
                  {timelineData.map((item, index) => (
                    <div key={index} className="flex">
                      <div className="mr-4 relative">
                        <div className={`p-2 rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                          <item.icon size={16} />
                        </div>
                        {index < timelineData.length - 1 && (
                          <div className={`absolute top-9 bottom-0 left-1/2 w-0.5 -ml-px ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
                        )}
                      </div>
                      <div className="pb-4">
                        <p className="font-medium">{item.event}</p>
                        <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          {item.description}
                        </p>
                        <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'} mt-1`}>
                          {item.date}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="ghost" fullWidth className="mt-2">View All Activity</Button>
              </Card>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <Card title="Engagement Stats">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="text-center p-3 rounded-lg bg-opacity-10 bg-blue-500">
                      <p className="text-2xl font-bold">12</p>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Emails Sent
                      </p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-opacity-10 bg-green-500">
                      <p className="text-2xl font-bold">8</p>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Emails Opened
                      </p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-opacity-10 bg-purple-500">
                      <p className="text-2xl font-bold">3</p>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Meetings
                      </p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-opacity-10 bg-yellow-500">
                      <p className="text-2xl font-bold">2</p>
                      <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Proposals
                      </p>
                    </div>
                  </div>
                </Card>
                
                <Card title="Notes">
                  <div className="space-y-2">
                    {lead.notes ? (
                      <div className={`p-3 rounded-lg text-sm ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                        <p>{lead.notes}</p>
                      </div>
                    ) : (
                      <>
                        <div className={`p-3 rounded-lg text-sm ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                          <p>Client mentioned they are looking to expand their tech team in Q3.</p>
                          <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mt-1`}>
                            Added yesterday
                          </p>
                        </div>
                        <div className={`p-3 rounded-lg text-sm ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                          <p>Currently using a competitor solution but contract expires in 60 days.</p>
                          <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mt-1`}>
                            Added 3 days ago
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                  <div className="mt-3">
                    <Button variant="outline" fullWidth size="sm">
                      Add Note
                    </Button>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        );
      
      case 'activity':
        return (
          <Card>
            <h4 className="font-medium mb-4">All Activities</h4>
            <div className="space-y-4">
              {[...timelineData, ...timelineData].map((item, index) => (
                <div key={index} className="flex pb-4 border-b last:border-b-0">
                  <div className="mr-4">
                    <div className={`p-2 rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <item.icon size={16} />
                    </div>
                  </div>
                  <div>
                    <p className="font-medium">{item.event}</p>
                    <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {item.description}
                    </p>
                    <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'} mt-1`}>
                      {item.date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        );
      
      case 'engagements':
        return (
          <div className="space-y-4">
            <Card title="Email Engagements">
              <div className="space-y-3">
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} border-l-4 border-green-500`}>
                  <div className="flex justify-between mb-1">
                    <p className="font-medium">Follow-up: Project Timeline</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>3 days ago</p>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Opened 2 times • Clicked link • Replied
                  </p>
                </div>
                
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} border-l-4 border-yellow-500`}>
                  <div className="flex justify-between mb-1">
                    <p className="font-medium">Initial Contact: Service Offerings</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>1 week ago</p>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Opened 1 time • No reply
                  </p>
                </div>
                
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} border-l-4 border-red-500`}>
                  <div className="flex justify-between mb-1">
                    <p className="font-medium">New Features Announcement</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>2 weeks ago</p>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Not opened
                  </p>
                </div>
              </div>
              
              <Button variant="outline" fullWidth className="mt-3">
                Send New Email
              </Button>
            </Card>
            
            <Card title="Meetings">
              <div className="space-y-3">
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                  <div className="flex justify-between mb-1">
                    <p className="font-medium">Product Demo</p>
                    <div className="text-green-500 flex items-center text-xs">
                      <Verified size={14} className="mr-1" />
                      <span>Completed</span>
                    </div>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Apr 15, 2023 • 30 min • Virtual
                  </p>
                </div>
                
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                  <div className="flex justify-between mb-1">
                    <p className="font-medium">Follow-up Discussion</p>
                    <div className="text-blue-500 flex items-center text-xs">
                      <Calendar size={14} className="mr-1" />
                      <span>Scheduled</span>
                    </div>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    May 3, 2023 • 45 min • Virtual
                  </p>
                </div>
              </div>
              
              <Button variant="outline" fullWidth className="mt-3">
                Schedule Meeting
              </Button>
            </Card>
          </div>
        );
      
      case 'documents':
        return (
          <Card>
            <h4 className="font-medium mb-3">Shared Documents</h4>
            <div className="space-y-3">
              <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} flex justify-between items-center`}>
                <div className="flex items-center">
                  <div className="bg-blue-100 p-2 rounded mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <line x1="16" y1="13" x2="8" y2="13"></line>
                      <line x1="16" y1="17" x2="8" y2="17"></line>
                      <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">Service Proposal</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      Shared 3 days ago • PDF
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} flex justify-between items-center`}>
                <div className="flex items-center">
                  <div className="bg-green-100 p-2 rounded mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-600">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <path d="M12 18v-6"></path>
                      <path d="M8 18v-1"></path>
                      <path d="M16 18v-3"></path>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">Case Study: XYZ Project</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      Shared 1 week ago • XLSX
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} flex justify-between items-center`}>
                <div className="flex items-center">
                  <div className="bg-red-100 p-2 rounded mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-600">
                      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                      <polyline points="13 2 13 9 20 9"></polyline>
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">Product Brochure</p>
                    <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      Shared 2 weeks ago • PDF
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
            </div>
            <Button variant="outline" fullWidth className="mt-3">
              Share New Document
            </Button>
          </Card>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="flex justify-between items-center mb-4 pb-3 border-b">
        <h2 className="text-xl font-bold">{lead.name}</h2>
        <Button variant="ghost" size="sm" className="rounded-full" onClick={onClose}>
          <X size={20} />
        </Button>
      </div>
      
      <div className="mb-6">
        <div className="flex space-x-1 border-b">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === tab.id 
                  ? isDark
                    ? 'text-white border-b-2 border-blue-500'
                    : 'text-blue-600 border-b-2 border-blue-500'
                  : isDark
                    ? 'text-gray-400 hover:text-gray-300'
                    : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="overflow-auto max-h-[calc(80vh-180px)]">
        {renderTabContent()}
      </div>
      
      <div className="mt-6 pt-3 border-t flex justify-end space-x-2">
        <Button variant="outline" onClick={onClose}>Close</Button>
        <Button>Edit Lead</Button>
      </div>
    </Modal>
  );
};

export default LeadDetailsModal;