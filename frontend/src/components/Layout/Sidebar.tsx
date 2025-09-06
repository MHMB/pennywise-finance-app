import React from 'react';
import { NavLink } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTheme } from '../../contexts/ThemeContext';
import {
  HomeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CogIcon,
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
  const { t } = useLanguage();
  const { theme } = useTheme();

  const navigation = [
    { name: t('navigation.dashboard'), href: '/dashboard', icon: HomeIcon },
    { name: t('navigation.transactions'), href: '/transactions', icon: CurrencyDollarIcon },
    { name: t('navigation.budgets'), href: '/budgets', icon: ChartBarIcon },
    { name: t('navigation.reports'), href: '/reports', icon: DocumentTextIcon },
    { name: t('navigation.settings'), href: '/settings', icon: CogIcon },
  ];

  return (
    <div className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} w-64 min-h-screen shadow-lg`}>
      <div className="p-6">
        <h1 className="text-2xl font-bold text-blue-600">Pennywise</h1>
      </div>
      
      <nav className="mt-6">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-6 py-3 text-sm font-medium transition-colors duration-200 ${
                isActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : `${theme === 'dark' ? 'text-gray-300 hover:text-white hover:bg-gray-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;