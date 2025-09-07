import React from 'react';
import { useQuery } from 'react-query';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/apiService';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { t } = useLanguage();

  const { data: summary, isLoading: summaryLoading } = useQuery(
    'financial-summary',
    () => apiService.getFinancialSummary({ period: 'monthly' }),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: budgetStatus, isLoading: budgetLoading } = useQuery(
    'budget-status',
    () => apiService.getBudgetStatus({ period: 'monthly' }),
    {
      refetchInterval: 30000,
    }
  );

  const { data: recentTransactions, isLoading: transactionsLoading } = useQuery(
    'recent-transactions',
    () => apiService.getTransactions({ limit: 5 }),
    {
      refetchInterval: 30000,
    }
  );

  if (summaryLoading || budgetLoading || transactionsLoading) {
    return <LoadingSpinner size="lg" className="h-64" />;
  }

  const financialData = summary?.data;
  const budgetData = budgetStatus?.data;
  const transactions = recentTransactions?.data?.results || [];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('dashboard.welcome')}
        </h1>
        <p className="text-gray-600 mt-2">
          Here's an overview of your financial status
        </p>
      </div>

      {/* Financial Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.totalIncome')}
              </p>
              <p className="text-2xl font-semibold text-gray-900">
                ${financialData?.totals?.income || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingDownIcon className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.totalExpenses')}
              </p>
              <p className="text-2xl font-semibold text-gray-900">
                ${financialData?.totals?.expenses || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.netWorth')}
              </p>
              <p className={`text-2xl font-semibold ${
                (financialData?.totals?.net || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${financialData?.totals?.net || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.budgetStatus')}
              </p>
              <p className="text-2xl font-semibold text-gray-900">
                {budgetData?.length || 0} {t('budgets.title')}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart Placeholder */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('dashboard.monthlyTrends')}
          </h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Chart will be implemented here
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('dashboard.recentTransactions')}
          </h3>
          <div className="space-y-3">
            {transactions.length > 0 ? (
              transactions.map((transaction: any) => (
                <div key={transaction.id} className="flex items-center justify-between py-2 border-b border-gray-200">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {transaction.description}
                    </p>
                    <p className="text-xs text-gray-500">
                      {transaction.category} • {new Date(transaction.date).toLocaleDateString()}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${
                    transaction.is_income ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.is_income ? '+' : '-'}${transaction.amount}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">
                {t('transactions.noTransactions')}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Budget Status */}
      {budgetData && budgetData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('dashboard.budgetStatus')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {budgetData.map((budget: any) => (
              <div key={budget.budget_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{budget.category}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    budget.status === 'on_track' ? 'bg-green-100 text-green-800' :
                    budget.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {budget.status === 'on_track' ? t('budgets.onTrack') :
                     budget.status === 'warning' ? t('budgets.warning') :
                     t('budgets.exceeded')}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{t('budgets.currentSpending')}</span>
                    <span className="font-medium">${budget.current_spending}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{t('budgets.limit')}</span>
                    <span className="font-medium">${budget.limit}</span>
                  </div>
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
                  <div className="text-xs text-gray-500 text-center">
                    {budget.percentage_used.toFixed(1)}% {t('budgets.percentageUsed')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;