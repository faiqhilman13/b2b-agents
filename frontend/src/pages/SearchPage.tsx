import React, { useState } from 'react';
import { Search, Filter, UploadCloud, Download, ChevronDown, X } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { useTheme } from '../context/ThemeContext';

const SearchPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedFilters, setSelectedFilters] = useState<string[]>(['Industry: Technology', 'Location: US']);
  
  const mockResults = Array.from({ length: 5 }, (_, i) => ({
    id: i + 1,
    name: `Lead ${i + 1}`,
    company: ['Acme Inc.', 'Globex Corp', 'Initech', 'Massive Dynamic', 'Stark Industries'][i],
    industry: ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'][i],
    location: ['New York', 'San Francisco', 'Chicago', 'Boston', 'Austin'][i],
    employees: [Math.floor(Math.random() * 500) + 10, Math.floor(Math.random() * 1000) + 100, Math.floor(Math.random() * 5000) + 1000][i % 3],
    revenue: ['$1M-$5M', '$5M-$10M', '$10M-$50M', '$50M-$100M', '$100M+'][i],
  }));

  const removeFilter = (filter: string) => {
    setSelectedFilters(selectedFilters.filter(f => f !== filter));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Lead Search</h1>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            leftIcon={<UploadCloud size={16} />}
          >
            Import Leads
          </Button>
          <Button 
            leftIcon={<Download size={16} />}
          >
            Export Results
          </Button>
        </div>
      </div>
      
      <Card className="mb-6">
        <div className="space-y-5">
          <div className={`relative flex items-center ${isDark ? 'bg-gray-700' : 'bg-gray-100'} rounded-lg px-4 py-3`}>
            <Search size={20} className="text-gray-500 mr-3" />
            <input
              type="text"
              placeholder="Search for companies, contacts, or keywords..."
              className={`block w-full bg-transparent border-0 focus:ring-0 outline-none ${
                isDark ? 'placeholder-gray-400' : 'placeholder-gray-500'
              }`}
            />
          </div>
          
          <div className="flex flex-wrap gap-2">
            {/* Filter buttons */}
            <div className="flex flex-wrap gap-2">
              <Button 
                variant="outline" 
                rightIcon={<ChevronDown size={16} />}
                className={`${isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'}`}
              >
                Industry
              </Button>
              <Button 
                variant="outline" 
                rightIcon={<ChevronDown size={16} />}
                className={`${isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'}`}
              >
                Location
              </Button>
              <Button 
                variant="outline" 
                rightIcon={<ChevronDown size={16} />}
                className={`${isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'}`}
              >
                Company Size
              </Button>
              <Button 
                variant="outline" 
                rightIcon={<ChevronDown size={16} />}
                className={`${isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'}`}
              >
                Revenue
              </Button>
              <Button 
                variant="outline" 
                leftIcon={<Filter size={16} />}
                className={`${isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'}`}
              >
                More Filters
              </Button>
            </div>
          </div>
          
          {/* Applied filters */}
          {selectedFilters.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {selectedFilters.map((filter, index) => (
                <div 
                  key={index}
                  className={`
                    flex items-center px-3 py-1 rounded-full text-sm
                    ${isDark ? 'bg-gray-700 text-white' : 'bg-gray-200 text-gray-800'}
                  `}
                >
                  {filter}
                  <button 
                    onClick={() => removeFilter(filter)}
                    className="ml-1 p-0.5 rounded-full hover:bg-gray-600 hover:text-white"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
              <button 
                className={`text-sm underline ${isDark ? 'text-gray-400' : 'text-gray-500'} hover:text-blue-500`}
              >
                Clear All
              </button>
            </div>
          )}
          
          <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Showing 5 results of 124 matches
            </p>
          </div>
        </div>
      </Card>
      
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className={isDark ? 'bg-gray-700' : 'bg-gray-50'}>
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Company
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Industry
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Location
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Employees
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Revenue
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {mockResults.map((result) => (
                <tr 
                  key={result.id}
                  className={`hover:${isDark ? 'bg-gray-750' : 'bg-gray-50'} transition-colors cursor-pointer`}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {result.company}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.industry}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.employees}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.revenue}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Button size="sm">Add Lead</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing 1 to 5 of 124 results
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" disabled>Previous</Button>
            <Button variant="outline" size="sm" className={isDark ? 'bg-gray-700' : 'bg-gray-100'}>1</Button>
            <Button variant="outline" size="sm">2</Button>
            <Button variant="outline" size="sm">3</Button>
            <Button variant="outline" size="sm">Next</Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default SearchPage;