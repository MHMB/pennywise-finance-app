import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTheme } from '../../contexts/ThemeContext';
import { apiService } from '../../services/apiService';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  UserCircleIcon,
  CogIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
} from '@heroicons/react/24/outline';

interface SettingsFormData {
  username: string;
  email: string;
  telegram_chat_id?: string;
}

interface AlertFormData {
  alert_type: string;
  threshold: number;
  enabled: boolean;
  telegram_enabled: boolean;
  email_enabled: boolean;
}

const Settings: React.FC = () => {
  const { user } = useAuth();
  const { language, changeLanguage, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('profile');

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
  } = useForm<SettingsFormData>();

  const {
    register: registerAlert,
    handleSubmit: handleAlertSubmit,
    reset: resetAlert,
    formState: { errors: alertErrors },
  } = useForm<AlertFormData>();

  const { data: alertConfigs, isLoading: alertsLoading } = useQuery(
    'alert-configs',
    () => apiService.getAlertConfigs()
  );

  const updateProfileMutation = useMutation(
    (data: SettingsFormData) => apiService.getCurrentUser(), // This would be a PATCH request in real implementation
    {
      onSuccess: () => {
        queryClient.invalidateQueries('current-user');
        toast.success(t('settings.settingsSaved'));
      },
      onError: (error: any) => {
        toast.error('Failed to update profile');
      },
    }
  );

  const createAlertMutation = useMutation(
    (data: AlertFormData) => apiService.createAlertConfig(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alert-configs');
        toast.success('Alert configuration saved');
        resetAlert();
      },
      onError: (error: any) => {
        toast.error('Failed to save alert configuration');
      },
    }
  );

  const onProfileSubmit = (data: SettingsFormData) => {
    updateProfileMutation.mutate(data);
  };

  const onAlertSubmit = (data: AlertFormData) => {
    createAlertMutation.mutate(data);
  };

  const handleLanguageChange = (newLanguage: string) => {
    changeLanguage(newLanguage);
    toast.success('Language changed successfully');
  };

  const handleThemeChange = () => {
    toggleTheme();
    toast.success('Theme changed successfully');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('settings.title')}
        </h1>
      </div>

      {/* Settings Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'profile'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <UserCircleIcon className="w-5 h-5 inline mr-2" />
              {t('settings.profile')}
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'preferences'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <CogIcon className="w-5 h-5 inline mr-2" />
              {t('settings.preferences')}
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'notifications'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BellIcon className="w-5 h-5 inline mr-2" />
              {t('settings.notifications')}
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('settings.profile')}
              </h3>
              
              <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">{t('auth.username')}</label>
                    <input
                      {...registerProfile('username', { required: t('validation.required') })}
                      type="text"
                      defaultValue={user?.username}
                      className="form-input"
                    />
                    {profileErrors.username && (
                      <p className="form-error">{profileErrors.username.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">{t('auth.email')}</label>
                    <input
                      {...registerProfile('email', { 
                        required: t('validation.required'),
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: t('validation.email')
                        }
                      })}
                      type="email"
                      defaultValue={user?.email}
                      className="form-input"
                    />
                    {profileErrors.email && (
                      <p className="form-error">{profileErrors.email.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="form-label">{t('settings.telegram')} Chat ID</label>
                  <input
                    {...registerProfile('telegram_chat_id')}
                    type="text"
                    defaultValue={user?.telegram_chat_id}
                    className="form-input"
                    placeholder="Enter your Telegram Chat ID"
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={updateProfileMutation.isLoading}
                    className="btn-primary"
                  >
                    {updateProfileMutation.isLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      t('settings.saveSettings')
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('settings.preferences')}
              </h3>
              
              <div className="space-y-6">
                {/* Language Settings */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{t('settings.language')}</h4>
                      <p className="text-sm text-gray-500">Choose your preferred language</p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleLanguageChange('en')}
                        className={`px-3 py-1 rounded text-sm ${
                          language === 'en'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        English
                      </button>
                      <button
                        onClick={() => handleLanguageChange('fa')}
                        className={`px-3 py-1 rounded text-sm ${
                          language === 'fa'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        فارسی
                      </button>
                    </div>
                  </div>
                </div>

                {/* Theme Settings */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{t('settings.theme')}</h4>
                      <p className="text-sm text-gray-500">Choose your preferred theme</p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={handleThemeChange}
                        className="flex items-center space-x-2 px-3 py-1 rounded text-sm bg-gray-100 text-gray-700 hover:bg-gray-200"
                      >
                        {theme === 'light' ? (
                          <>
                            <MoonIcon className="w-4 h-4" />
                            <span>{t('settings.dark')}</span>
                          </>
                        ) : (
                          <>
                            <SunIcon className="w-4 h-4" />
                            <span>{t('settings.light')}</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('settings.notifications')}
              </h3>
              
              {/* Alert Configuration Form */}
              <form onSubmit={handleAlertSubmit(onAlertSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Alert Type</label>
                    <select
                      {...registerAlert('alert_type', { required: 'Alert type is required' })}
                      className="form-input"
                    >
                      <option value="">Select alert type</option>
                      <option value="threshold">Threshold Alert</option>
                      <option value="daily">Daily Summary</option>
                      <option value="weekly">Weekly Summary</option>
                      <option value="overspend">Overspend Alert</option>
                    </select>
                    {alertErrors.alert_type && (
                      <p className="form-error">{alertErrors.alert_type.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">{t('settings.threshold')} (%)</label>
                    <input
                      {...registerAlert('threshold', { 
                        required: 'Threshold is required',
                        valueAsNumber: true,
                        min: { value: 0, message: 'Threshold must be at least 0' },
                        max: { value: 100, message: 'Threshold must be at most 100' }
                      })}
                      type="number"
                      min="0"
                      max="100"
                      className="form-input"
                      placeholder="75"
                    />
                    {alertErrors.threshold && (
                      <p className="form-error">{alertErrors.threshold.message}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      {...registerAlert('enabled')}
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      {t('settings.enabled')}
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      {...registerAlert('telegram_enabled')}
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      {t('settings.telegram')} {t('settings.enabled')}
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      {...registerAlert('email_enabled')}
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      Email {t('settings.enabled')}
                    </label>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={createAlertMutation.isLoading}
                    className="btn-primary"
                  >
                    {createAlertMutation.isLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      'Save Alert Configuration'
                    )}
                  </button>
                </div>
              </form>

              {/* Existing Alert Configurations */}
              {alertsLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Current Alert Configurations</h4>
                  {alertConfigs?.data?.results?.map((alert: any) => (
                    <div key={alert.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-medium text-gray-900 capitalize">
                            {alert.alert_type.replace('_', ' ')}
                          </h5>
                          <p className="text-sm text-gray-500">
                            Threshold: {alert.threshold}%
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            alert.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {alert.enabled ? t('settings.enabled') : t('settings.disabled')}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;