import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { useDropzone } from 'react-dropzone';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/apiService';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  ArrowUpTrayIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

interface TransactionFormData {
  amount: number;
  description: string;
  category: string;
  date: string;
  is_income: boolean;
}

const Transactions: React.FC = () => {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<any>(null);
  const [showImportModal, setShowImportModal] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<TransactionFormData>();

  const { data: transactions, isLoading } = useQuery(
    'transactions',
    () => apiService.getTransactions(),
    {
      refetchInterval: 30000,
    }
  );

  const { data: categories } = useQuery(
    'transaction-categories',
    () => apiService.getTransactionCategories()
  );

  const createTransactionMutation = useMutation(
    (data: TransactionFormData) => apiService.createTransaction(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('transactions');
        toast.success(t('transactions.transactionAdded'));
        setShowAddForm(false);
        reset();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to create transaction');
      },
    }
  );

  const updateTransactionMutation = useMutation(
    ({ id, data }: { id: number; data: TransactionFormData }) =>
      apiService.updateTransaction(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('transactions');
        toast.success(t('transactions.transactionUpdated'));
        setEditingTransaction(null);
        reset();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to update transaction');
      },
    }
  );

  const deleteTransactionMutation = useMutation(
    (id: number) => apiService.deleteTransaction(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('transactions');
        toast.success(t('transactions.transactionDeleted'));
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to delete transaction');
      },
    }
  );

  const importCSVMutation = useMutation(
    (file: File) => apiService.importTransactionsCSV(file),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries('transactions');
        toast.success(t('transactions.csvImported'));
        setShowImportModal(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || t('transactions.csvImportError'));
      },
    }
  );

  const onSubmit = (data: TransactionFormData) => {
    if (editingTransaction) {
      updateTransactionMutation.mutate({ id: editingTransaction.id, data });
    } else {
      createTransactionMutation.mutate(data);
    }
  };

  const handleEdit = (transaction: any) => {
    setEditingTransaction(transaction);
    setValue('amount', transaction.amount);
    setValue('description', transaction.description);
    setValue('category', transaction.category);
    setValue('date', transaction.date);
    setValue('is_income', transaction.is_income);
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      deleteTransactionMutation.mutate(id);
    }
  };

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      importCSVMutation.mutate(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  if (isLoading) {
    return <LoadingSpinner size="lg" className="h-64" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('transactions.title')}
        </h1>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="btn-secondary flex items-center"
          >
            <ArrowUpTrayIcon className="w-4 h-4 mr-2" />
            {t('transactions.importCSV')}
          </button>
          <button
            onClick={() => {
              setShowAddForm(true);
              setEditingTransaction(null);
              reset();
            }}
            className="btn-primary flex items-center"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            {t('transactions.addTransaction')}
          </button>
        </div>
      </div>

      {/* Add/Edit Transaction Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingTransaction ? t('transactions.editTransaction') : t('transactions.addTransaction')}
          </h3>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">{t('transactions.amount')}</label>
                <input
                  {...register('amount', { 
                    required: t('validation.required'),
                    valueAsNumber: true,
                    min: { value: 0.01, message: t('validation.positive') }
                  })}
                  type="number"
                  step="0.01"
                  className="form-input"
                  placeholder="0.00"
                />
                {errors.amount && (
                  <p className="form-error">{errors.amount.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">{t('transactions.date')}</label>
                <input
                  {...register('date', { required: t('validation.required') })}
                  type="date"
                  className="form-input"
                />
                {errors.date && (
                  <p className="form-error">{errors.date.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="form-label">{t('transactions.description')}</label>
              <input
                {...register('description', { required: t('validation.required') })}
                type="text"
                className="form-input"
                placeholder="Transaction description"
              />
              {errors.description && (
                <p className="form-error">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">{t('transactions.category')}</label>
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
                <label className="form-label">{t('transactions.type')}</label>
                <select
                  {...register('is_income', { valueAsNumber: true })}
                  className="form-input"
                >
                  <option value={0}>{t('transactions.expense')}</option>
                  <option value={1}>{t('transactions.income')}</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setEditingTransaction(null);
                  reset();
                }}
                className="btn-secondary"
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                disabled={createTransactionMutation.isLoading || updateTransactionMutation.isLoading}
                className="btn-primary"
              >
                {(createTransactionMutation.isLoading || updateTransactionMutation.isLoading) ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  editingTransaction ? t('common.save') : t('transactions.addTransaction')
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Transactions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            {t('transactions.title')}
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>{t('transactions.date')}</th>
                <th>{t('transactions.description')}</th>
                <th>{t('transactions.category')}</th>
                <th>{t('transactions.type')}</th>
                <th>{t('transactions.amount')}</th>
                <th className="no-print">{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {transactions?.data?.results?.map((transaction: any) => (
                <tr key={transaction.id}>
                  <td>{new Date(transaction.date).toLocaleDateString()}</td>
                  <td>{transaction.description}</td>
                  <td>{transaction.category}</td>
                  <td>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      transaction.is_income 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.is_income ? t('transactions.income') : t('transactions.expense')}
                    </span>
                  </td>
                  <td className={`font-medium ${
                    transaction.is_income ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.is_income ? '+' : '-'}${transaction.amount}
                  </td>
                  <td className="no-print">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(transaction)}
                        className="text-blue-600 hover:text-blue-800"
                        title={t('transactions.editTransaction')}
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(transaction.id)}
                        className="text-red-600 hover:text-red-800"
                        title={t('transactions.deleteTransaction')}
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* CSV Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {t('transactions.importCSV')}
              </h3>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer ${
                  isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                }`}
              >
                <input {...getInputProps()} />
                <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">
                  {isDragActive
                    ? 'Drop the CSV file here...'
                    : 'Drag and drop a CSV file here, or click to select'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  CSV files only
                </p>
              </div>

              {importCSVMutation.isLoading && (
                <div className="mt-4 text-center">
                  <LoadingSpinner size="sm" />
                  <p className="text-sm text-gray-600 mt-2">Processing CSV...</p>
                </div>
              )}

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowImportModal(false)}
                  className="btn-secondary"
                  disabled={importCSVMutation.isLoading}
                >
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;