import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string | null) {
    if (token) {
      this.api.defaults.headers.Authorization = `Token ${token}`;
    } else {
      delete this.api.defaults.headers.Authorization;
    }
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<AxiosResponse> {
    return this.api.post('/auth/login/', { username, password });
  }

  async register(userData: any): Promise<AxiosResponse> {
    return this.api.post('/users/register/', userData);
  }

  // User endpoints
  async getCurrentUser(): Promise<AxiosResponse> {
    return this.api.get('/users/me/');
  }

  // Transaction endpoints
  async getTransactions(params?: any): Promise<AxiosResponse> {
    return this.api.get('/transactions/', { params });
  }

  async createTransaction(data: any): Promise<AxiosResponse> {
    return this.api.post('/transactions/', data);
  }

  async updateTransaction(id: number, data: any): Promise<AxiosResponse> {
    return this.api.patch(`/transactions/${id}/`, data);
  }

  async deleteTransaction(id: number): Promise<AxiosResponse> {
    return this.api.delete(`/transactions/${id}/`);
  }

  async getTransactionSummary(params?: any): Promise<AxiosResponse> {
    return this.api.get('/transactions/summary/', { params });
  }

  async getTransactionCategories(): Promise<AxiosResponse> {
    return this.api.get('/transactions/categories/');
  }

  async importTransactionsCSV(file: File): Promise<AxiosResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.api.post('/transactions/import_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async bulkCreateTransactions(transactions: any[]): Promise<AxiosResponse> {
    return this.api.post('/transactions/bulk_create/', { transactions });
  }

  // Budget endpoints
  async getBudgets(): Promise<AxiosResponse> {
    return this.api.get('/budgets/');
  }

  async createBudget(data: any): Promise<AxiosResponse> {
    return this.api.post('/budgets/', data);
  }

  async updateBudget(id: number, data: any): Promise<AxiosResponse> {
    return this.api.patch(`/budgets/${id}/`, data);
  }

  async deleteBudget(id: number): Promise<AxiosResponse> {
    return this.api.delete(`/budgets/${id}/`);
  }

  async getBudgetStatus(params?: any): Promise<AxiosResponse> {
    return this.api.get('/budgets/status/', { params });
  }

  async getBudgetAlerts(): Promise<AxiosResponse> {
    return this.api.get('/budgets/alerts/');
  }

  async getBudgetRecommendations(params?: any): Promise<AxiosResponse> {
    return this.api.get('/budgets/recommendations/', { params });
  }

  // Report endpoints
  async getFinancialSummary(params?: any): Promise<AxiosResponse> {
    return this.api.get('/reports/summary/', { params });
  }

  async getCategoryBreakdown(params?: any): Promise<AxiosResponse> {
    return this.api.get('/reports/category/', { params });
  }

  async getMonthlyTrends(params?: any): Promise<AxiosResponse> {
    return this.api.get('/reports/trends/', { params });
  }

  async getBudgetPerformance(params?: any): Promise<AxiosResponse> {
    return this.api.get('/reports/budget/', { params });
  }

  // Chart endpoints
  async getPieChart(params?: any): Promise<AxiosResponse> {
    return this.api.get('/charts/pie/', { params });
  }

  async getBarChart(params?: any): Promise<AxiosResponse> {
    return this.api.get('/charts/bar/', { params });
  }

  async getLineChart(params?: any): Promise<AxiosResponse> {
    return this.api.get('/charts/line/', { params });
  }

  async getDashboardChart(): Promise<AxiosResponse> {
    return this.api.get('/charts/dashboard/');
  }

  async getBudgetChart(params?: any): Promise<AxiosResponse> {
    return this.api.get('/charts/budget/', { params });
  }

  async downloadChart(type: string, params?: any): Promise<AxiosResponse> {
    return this.api.get('/charts/download/', { 
      params: { type, ...params },
      responseType: 'blob'
    });
  }

  // Alert endpoints
  async getAlertConfigs(): Promise<AxiosResponse> {
    return this.api.get('/alert-configs/');
  }

  async createAlertConfig(data: any): Promise<AxiosResponse> {
    return this.api.post('/alert-configs/', data);
  }

  async updateAlertConfig(id: number, data: any): Promise<AxiosResponse> {
    return this.api.patch(`/alert-configs/${id}/`, data);
  }

  async deleteAlertConfig(id: number): Promise<AxiosResponse> {
    return this.api.delete(`/alert-configs/${id}/`);
  }
}

export const apiService = new ApiService();