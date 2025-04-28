import React, { useState } from 'react';
import { Bell, Search, Moon, Sun, Menu, User } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const isDark = theme === 'dark';
  const baseClasses = isDark 
    ? 'bg-gray-800 text-gray-200 border-gray-700'
    : 'bg-white text-gray-800 border-gray-200';

  return (
    <header className={`${baseClasses} h-16 border-b flex items-center justify-between px-4 md:px-6`}>
      <div className="flex items-center md:hidden">
        <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
          <Menu size={20} />
        </button>
      </div>
      
      <div className="hidden md:flex flex-1 max-w-md">
        <div className={`flex items-center w-full px-4 py-2 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <Search size={18} className="text-gray-500" />
          <input
            type="text"
            placeholder="Search..."
            className={`ml-2 outline-none border-none bg-transparent w-full ${isDark ? 'placeholder-gray-400' : 'placeholder-gray-500'}`}
          />
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <button className={`p-2 rounded-full ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}>
          <Bell size={20} />
        </button>
        
        <button 
          className={`p-2 rounded-full ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          onClick={toggleTheme}
        >
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        
        <div className="relative">
          <button 
            className="flex items-center p-1"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
              <User size={16} className="text-white" />
            </div>
          </button>
          
          {showUserMenu && (
            <div 
              className={`absolute right-0 mt-2 w-48 py-2 rounded-md shadow-lg ${baseClasses}`}
            >
              <a href="#profile" className="block px-4 py-2 hover:bg-blue-600 hover:text-white">
                Your Profile
              </a>
              <a href="#settings" className="block px-4 py-2 hover:bg-blue-600 hover:text-white">
                Settings
              </a>
              <a href="#signout" className="block px-4 py-2 hover:bg-blue-600 hover:text-white">
                Sign out
              </a>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;