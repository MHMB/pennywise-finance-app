import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/apiService';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  DocumentTextIcon,
  ChartBarIcon,
  DownloadIcon,
} from '@heroicons/react/24/outline';

const Reports: React.FC = () => {
  const { t } = useLanguage();
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [selectedReport, setSelectedReport] = useState('summary');

  const { data: financialSummary, isLoading: summaryLoading } = useQuery(
    ['financial-summary', selectedPeriod],
    () => apiService.getFinancialSummary({ period: selectedPeriod }),
    {
      enabled: selectedReport === 'summary',
    }
  );

  const { data: categoryBreakdown, isLoading: breakdownLoading } = useQuery(
    ['category-breakdown', selectedPeriod],
    () => apiService.getCategoryBreakdown({ period: selectedPeriod }),
    {
      enabled: selectedReport === 'category',
    }
  );

  const { data: monthlyTrends, isLoading: trendsLoading } = useQuery(
    'monthly-trends',
    () => apiService.getMonthlyTrends({ months: 12 }),
    {
      enabled: selectedReport === 'trends',
    }
  );

  const { data: budgetPerformance, isLoading: budgetLoading } = useQuery(
    ['budget-performance', selectedPeriod],
    () => apiService.getBudgetPerformance({ period: selectedPeriod }),
    {
      enabled: selectedReport === 'budget',
    }
  );

  const isLoading = summaryLoading || breakdownLoading || trendsLoading || budgetLoading;

  const renderReport = () => {
    switch (selectedReport) {
      case 'summary':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('reports.financialSummary')}
            </h3>
            {financialSummary?.data && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">
                    {t('dashboard.totalIncome')}
                  </h4>
                  <p className="text-2xl font-bold text-green-600">
                    ${financialSummary.data.totals?.income || 0}
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">
                    {t('dashboard.totalExpenses')}
                  </h4>
                  <p className="text-2xl font-bold text-red-600">
                    ${financialSummary.data.totals?.expenses || 0}
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">
                    {t('dashboard.netWorth')}
                  </h4>
                  <p className={`text-2xl font-bold ${
                    (financialSummary.data.totals?.net || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${financialSummary.data.totals?.net || 0}
                  </p>
                </div>
              </div>
            )}
          </div>
        );

      case 'category':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('reports.categoryBreakdown')}
            </h3>
            {categoryBreakdown?.data?.breakdown && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="table">
                  <thead>
                    <tr>
                      <th>{t('transactions.category')}</th>
                      <th>{t('transactions.amount')}</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryBreakdown.data.breakdown.map((item: any, index: number) => (
                      <tr key={index}>
                        <td>{item.category}</td>
                        <td>${item.total}</td>
                        <td>{item.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );

      case 'trends':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('reports.monthlyTrends')}
            </h3>
            {monthlyTrends?.data?.trends && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>{t('transactions.income')}</th>
                      <th>{t('transactions.expense')}</th>
                      <th>Net</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monthlyTrends.data.trends.map((trend: any, index: number) => (
                      <tr key={index}>
                        <td>{trend.month_name}</td>
                        <td className="text-green-600">${trend.income}</td>
                        <td className="text-red-600">${trend.expenses}</td>
                        <td className={`font-medium ${
                          trend.net >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          ${trend.net}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );

      case 'budget':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('reports.budgetPerformance')}
            </h3>
            {budgetPerformance?.data?.performance && (
              <div className="space-y-4">
                {budgetPerformance.data.performance.map((budget: any, index: number) => (
                  <div key={index} className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h4 className="text-lg font-medium text-gray-900">
                        {budget.category}
                      </h4>
                      <span className={`px-3 py-1 text-sm rounded-full ${
                        budget.status === 'on_track' ? 'bg-green-100 text-green-800' :
                        budget.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {budget.status === 'on_track' ? t('budgets.onTrack') :
                         budget.status === 'warning' ? t('budgets.warning') :
                         t('budgets.exceeded')}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">{t('budgets.limit')}</p>
                        <p className="text-lg font-semibold">${budget.limit}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">{t('budgets.currentSpending')}</p>
                        <p className="text-lg font-semibold">${budget.current_spending}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">{t('budgets.percentageUsed')}</p>
                        <p className="text-lg font-semibold">{budget.percentage_used.toFixed(1)}%</p>
                      </div>
                    </div>
                    <div className="mt-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            budget.percentage_used <= 75 ? 'bg-green-500' :
                            budget.percentage_used <= 90 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('reports.title')}
        </h1>
        <div className="flex space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="form-input"
          >
            <option value="daily">{t('reports.daily')}</option>
            <option value="weekly">{t('reports.weekly')}</option>
            <option value="monthly">{t('reports.monthly')}</option>
            <option value="yearly">{t('reports.yearly')}</option>
          </select>
          <button className="btn-secondary flex items-center">
            <DownloadIcon className="w-4 h-4 mr-2" />
            {t('reports.downloadReport')}
          </button>
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Select Report Type
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button
            onClick={() => setSelectedReport('summary')}
            className={`p-4 rounded-lg border-2 text-center transition-colors ${
              selectedReport === 'summary'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <DocumentTextIcon className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">{t('reports.financialSummary')}</p>
          </button>
          
          <button
            onClick={() => setSelectedReport('category')}
            className={`p-4 rounded-lg border-2 text-center transition-colors ${
              selectedReport === 'category'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <ChartBarIcon className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">{t('reports.categoryBreakdown')}</p>
          </button>
          
          <button
            onClick={() => setSelectedReport('trends')}
            className={`p-4 rounded-lg border-2 text-center transition-colors ${
              selectedReport === 'trends'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <ChartBarIcon className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">{t('reports.monthlyTrends')}</p>
          </button>
          
          <button
            onClick={() => setSelectedReport('budget')}
            className={`p-4 rounded-lg border-2 text-center transition-colors ${
              selectedReport === 'budget'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <ChartBarIcon className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">{t('reports.budgetPerformance')}</p>
          </button>
        </div>
      </div>

      {/* Report Content */}
      <div className="bg-white rounded-lg shadow p-6">
        {isLoading ? (
          <LoadingSpinner size="lg" className="h-64" />
        ) : (
          renderReport()
        )}
      </div>
    </div>
  );
};

export default Reports;