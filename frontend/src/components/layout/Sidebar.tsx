import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Search, Users, Mail, FileText, 
  GitBranch, Settings, Database, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { theme } = useTheme();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/search', label: 'Search', icon: <Search size={20} /> },
    { path: '/leads', label: 'Leads', icon: <Users size={20} /> },
    { path: '/campaigns', label: 'Campaigns', icon: <Mail size={20} /> },
    { path: '/proposals', label: 'Proposals', icon: <FileText size={20} /> },
    { path: '/workflow', label: 'Workflow', icon: <GitBranch size={20} /> },
    { path: '/enrichment', label: 'Enrichment', icon: <Database size={20} /> },
    { path: '/settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  const baseClasses = theme === 'dark' 
    ? 'bg-gray-800 text-gray-200 border-gray-700'
    : 'bg-white text-gray-800 border-gray-200';

  return (
    <>
      <div 
        className={`${baseClasses} h-screen border-r transition-all duration-300 ease-in-out ${
          collapsed ? 'w-16' : 'w-64'
        } fixed left-0 top-0 z-20`}
      >
        <div className={`flex items-center justify-between h-16 ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'} px-4`}>
          {!collapsed && (
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-lg bg-green-500 flex items-center justify-center mr-2">
                <span className="text-white font-bold">L</span>
              </div>
              <span className="font-bold text-lg">LeadFlow</span>
            </div>
          )}
          <button 
            onClick={() => setCollapsed(!collapsed)}
            className={`p-1 rounded-md ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'} transition-colors`}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        </div>

        <div className="py-4">
          <ul className="space-y-2 px-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => `
                    flex items-center py-2 px-3 rounded-lg transition-colors duration-200
                    ${isActive 
                      ? `text-white bg-green-600 hover:bg-green-700` 
                      : `${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`
                    }
                  `}
                >
                  <span className="mr-3">{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className={`transition-all duration-300 ease-in-out ${collapsed ? 'w-16' : 'w-64'}`} />
    </>
  );
};

export default Sidebar;