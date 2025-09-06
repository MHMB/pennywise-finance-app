import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  SunIcon, 
  MoonIcon, 
  GlobeAltIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { language, changeLanguage } = useLanguage();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = () => {
    logout();
  };

  const toggleLanguage = () => {
    changeLanguage(language === 'en' ? 'fa' : 'en');
  };

  return (
    <header className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-sm border-b border-gray-200`}>
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.username}
            </h2>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors duration-200"
              title={language === 'en' ? 'Switch to Persian' : 'Switch to English'}
            >
              <GlobeAltIcon className="w-5 h-5 text-gray-600" />
            </button>
            
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors duration-200"
              title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            >
              {theme === 'light' ? (
                <MoonIcon className="w-5 h-5 text-gray-600" />
              ) : (
                <SunIcon className="w-5 h-5 text-gray-600" />
              )}
            </button>
            
            {/* User Menu */}
            <div className="flex items-center space-x-2">
              <UserCircleIcon className="w-8 h-8 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                {user?.email}
              </span>
            </div>
            
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors duration-200"
              title="Logout"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;