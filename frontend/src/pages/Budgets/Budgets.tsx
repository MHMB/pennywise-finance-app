import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/apiService';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

interface BudgetFormData {
  category: string;
  limit: number;
  period: string;
}

const Budgets: React.FC = () => {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingBudget, setEditingBudget] = useState<any>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<BudgetFormData>();

  const { data: budgets, isLoading } = useQuery(
    'budgets',
    () => apiService.getBudgets(),
    {
      refetchInterval: 30000,
    }
  );

  const { data: budgetStatus } = useQuery(
    'budget-status',
    () => apiService.getBudgetStatus({ period: 'monthly' }),
    {
      refetchInterval: 30000,
    }
  );

  const { data: categories } = useQuery(
    'transaction-categories',
    () => apiService.getTransactionCategories()
  );

  const createBudgetMutation = useMutation(
    (data: BudgetFormData) => apiService.createBudget(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
        queryClient.invalidateQueries('budget-status');
        toast.success(t('budgets.budgetAdded'));
        setShowAddForm(false);
        reset();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to create budget');
      },
    }
  );

  const updateBudgetMutation = useMutation(
    ({ id, data }: { id: number; data: BudgetFormData }) =>
      apiService.updateBudget(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
        queryClient.invalidateQueries('budget-status');
        toast.success(t('budgets.budgetUpdated'));
        setEditingBudget(null);
        reset();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to update budget');
      },
    }
  );

  const deleteBudgetMutation = useMutation(
    (id: number) => apiService.deleteBudget(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('budgets');
        queryClient.invalidateQueries('budget-status');
        toast.success(t('budgets.budgetDeleted'));
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to delete budget');
      },
    }
  );

  const onSubmit = (data: BudgetFormData) => {
    if (editingBudget) {
      updateBudgetMutation.mutate({ id: editingBudget.id, data });
    } else {
      createBudgetMutation.mutate(data);
    }
  };

  const handleEdit = (budget: any) => {
    setEditingBudget(budget);
    setValue('category', budget.category);
    setValue('limit', budget.limit);
    setValue('period', budget.period);
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this budget?')) {
      deleteBudgetMutation.mutate(id);
    }
  };

  const getBudgetStatus = (budgetId: number) => {
    return budgetStatus?.data?.find((status: any) => status.budget_id === budgetId);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'exceeded':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'on_track':
        return t('budgets.onTrack');
      case 'warning':
        return t('budgets.warning');
      case 'exceeded':
        return t('budgets.exceeded');
      default:
        return status;
    }
  };

  if (isLoading) {
    return <LoadingSpinner size="lg" className="h-64" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('budgets.title')}
        </h1>
        <button
          onClick={() => {
            setShowAddForm(true);
            setEditingBudget(null);
            reset();
          }}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          {t('budgets.addBudget')}
        </button>
      </div>

      {/* Add/Edit Budget Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingBudget ? t('budgets.editBudget') : t('budgets.addBudget')}
          </h3>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="form-label">{t('budgets.category')}</label>
                <select
                  {...register('category', { required: t('validation.required') })}
                  className="form-input"
                >
                  <option value="">Select category</option>
                  {categories?.data?.categories?.map((category: string) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="form-error">{errors.category.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">{t('budgets.limit')}</label>
                <input
                  {...register('limit', { 
                    required: t('validation.required'),
                    valueAsNumber: true,
                    min: { value: 0.01, message: t('validation.positive') }
                  })}
                  type="number"
                  step="0.01"
                  className="form-input"
                  placeholder="0.00"
                />
                {errors.limit && (
                  <p className="form-error">{errors.limit.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">{t('budgets.period')}</label>
                <select
                  {...register('period', { required: t('validation.required') })}
                  className="form-input"
                >
                  <option value="weekly">{t('budgets.weekly')}</option>
                  <option value="monthly">{t('budgets.monthly')}</option>
                  <option value="yearly">{t('budgets.yearly')}</option>
                </select>
                {errors.period && (
                  <p className="form-error">{errors.period.message}</p>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setEditingBudget(null);
                  reset();
                }}
                className="btn-secondary"
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                disabled={createBudgetMutation.isLoading || updateBudgetMutation.isLoading}
                className="btn-primary"
              >
                {(createBudgetMutation.isLoading || updateBudgetMutation.isLoading) ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  editingBudget ? t('common.save') : t('budgets.addBudget')
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Budget Status Overview */}
      {budgetStatus && budgetStatus.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('budgets.status')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {budgetStatus.map((status: any) => (
              <div key={status.budget_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{status.category}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    status.status === 'on_track' ? 'bg-green-100 text-green-800' :
                    status.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {getStatusText(status.status)}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{t('budgets.currentSpending')}</span>
                    <span className="font-medium">${status.current_spending}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{t('budgets.limit')}</span>
                    <span className="font-medium">${status.limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getStatusColor(status.status)}`}
                      style={{ width: `${Math.min(status.percentage_used, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 text-center">
                    {status.percentage_used.toFixed(1)}% {t('budgets.percentageUsed')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Budgets Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            {t('budgets.title')}
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>{t('budgets.category')}</th>
                <th>{t('budgets.limit')}</th>
                <th>{t('budgets.period')}</th>
                <th>{t('budgets.currentSpending')}</th>
                <th>{t('budgets.remainingBudget')}</th>
                <th>{t('budgets.percentageUsed')}</th>
                <th className="no-print">{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {budgets?.data?.results?.map((budget: any) => {
                const status = getBudgetStatus(budget.id);
                return (
                  <tr key={budget.id}>
                    <td>{budget.category}</td>
                    <td>${budget.limit}</td>
                    <td className="capitalize">{budget.period}</td>
                    <td>${status?.current_spending || 0}</td>
                    <td>${status?.remaining_budget || budget.limit}</td>
                    <td>
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full ${getStatusColor(status?.status || 'on_track')}`}
                            style={{ width: `${Math.min(status?.percentage_used || 0, 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm">
                          {(status?.percentage_used || 0).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="no-print">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(budget)}
                          className="text-blue-600 hover:text-blue-800"
                          title={t('budgets.editBudget')}
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(budget.id)}
                          className="text-red-600 hover:text-red-800"
                          title={t('budgets.deleteBudget')}
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {(!budgets?.data?.results || budgets.data.results.length === 0) && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {t('budgets.noBudgets')}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first budget.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              {t('budgets.addBudget')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;