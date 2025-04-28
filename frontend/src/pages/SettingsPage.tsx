import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Save, Key, Mail, Database, Bell, Users, Shield } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const SettingsPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <Button leftIcon={<Save size={16} />}>Save Changes</Button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-3">
          <Card className="sticky top-6">
            <nav className="space-y-1">
              {[
                { icon: Key, label: 'API Keys' },
                { icon: Mail, label: 'Email Settings' },
                { icon: Database, label: 'Data Sources' },
                { icon: Bell, label: 'Notifications' },
                { icon: Users, label: 'Team Members' },
                { icon: Shield, label: 'Security' },
              ].map((item, index) => (
                <button
                  key={index}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg w-full transition-colors ${
                    index === 0
                      ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : `${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`
                  }`}
                >
                  <item.icon size={18} className="mr-2" />
                  {item.label}
                </button>
              ))}
            </nav>
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-9 space-y-6">
          <Card>
            <h2 className="text-lg font-medium mb-4">API Keys</h2>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Production API Key
                </label>
                <div className="mt-1 flex rounded-md shadow-sm">
                  <input
                    type="password"
                    value="sk_live_123456789"
                    readOnly
                    className={`flex-1 block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                  <Button className="ml-2">
                    Reveal
                  </Button>
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Test API Key
                </label>
                <div className="mt-1 flex rounded-md shadow-sm">
                  <input
                    type="password"
                    value="sk_test_123456789"
                    readOnly
                    className={`flex-1 block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                  <Button className="ml-2">
                    Reveal
                  </Button>
                </div>
              </div>

              <div>
                <Button variant="outline">
                  Generate New Key
                </Button>
              </div>
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-medium mb-4">Webhook Settings</h2>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Webhook URL
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    placeholder="https://your-domain.com/webhook"
                    className={`block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Secret Key
                </label>
                <div className="mt-1">
                  <input
                    type="password"
                    className={`block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="enableWebhook"
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="enableWebhook" className="text-sm">
                  Enable webhook notifications
                </label>
              </div>
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-medium mb-4">Rate Limits</h2>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Requests per minute
                </label>
                <div className="mt-1">
                  <input
                    type="number"
                    defaultValue="60"
                    className={`block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Concurrent connections
                </label>
                <div className="mt-1">
                  <input
                    type="number"
                    defaultValue="10"
                    className={`block w-full rounded-md sm:text-sm border-gray-300 ${
                      isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50'
                    }`}
                  />
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;