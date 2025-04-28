import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

// API base URL - should be configurable based on environment
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS with credentials
  timeout: 15000, // 15 seconds timeout
});

// Helper to get cookie value
const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
};

// Request interceptor for adding auth token and CSRF token
apiClient.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    
    // Add authentication token
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add CSRF token for non-GET requests
    const method = config.method?.toUpperCase();
    if (method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const csrfToken = getCookie('csrf_token');
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      } else {
        console.warn('CSRF token not found in cookies');
      }
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status);
    return response;
  },
  async (error: AxiosError) => {
    console.error('Response error:', error.message, error.response?.status);
    
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Could implement token refresh logic here
        // const refreshToken = localStorage.getItem('refresh_token');
        // const response = await apiClient.post('/token/refresh', { refresh_token: refreshToken });
        // const { access_token } = response.data;
        // localStorage.setItem('auth_token', access_token);
        
        // For now, redirect to login
        window.location.href = '/login';
        return Promise.reject(error);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle CSRF errors - redirect to reload csrf token
    if (error.response?.status === 403 && 
        error.response?.data && 
        typeof (error.response.data as { detail?: string }).detail === 'string' &&
        (error.response.data as { detail: string }).detail.includes('CSRF')) {
      console.error('CSRF token validation failed. Reloading page to get a new token.');
      window.location.reload();
      return Promise.reject(error);
    }
    
    // Handle other errors
    return Promise.reject(error);
  }
);

// Type for API error response
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// Normalize error responses
const normalizeError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      status: error.response?.status || 500,
      message: error.response?.data?.detail || error.message,
      details: error.response?.data
    };
  }
  
  return {
    status: 500,
    message: error.message || 'Unknown error occurred',
  };
};

// API service with typed methods
const apiService = {
  // Authentication
  auth: {
    login: async (username: string, password: string) => {
      try {
        // Create form data for submission
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        // Set proper content type for form data
        const response = await apiClient.post('/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        console.log('Login response:', response.data);
        return response.data;
      } catch (error) {
        console.error('Login error:', error);
        throw normalizeError(error);
      }
    },
    
    getCurrentUser: async () => {
      try {
        const response = await apiClient.get('/users/me');
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },
  
  // Leads
  leads: {
    getAll: async (params?: { source?: string; limit?: number; offset?: number }) => {
      try {
        const response = await apiClient.get('/leads', { params });
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    getCount: async (source?: string) => {
      try {
        const response = await apiClient.get('/leads/count', {
          params: source ? { source } : undefined
        });
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    getById: async (id: string) => {
      try {
        const response = await apiClient.get(`/leads/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    create: async (leadData: any) => {
      try {
        const response = await apiClient.post('/leads', leadData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    update: async (id: string, leadData: any) => {
      try {
        const response = await apiClient.put(`/leads/${id}`, leadData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    delete: async (id: string) => {
      try {
        const response = await apiClient.delete(`/leads/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },
  
  // Dashboard
  dashboard: {
    getStatistics: async () => {
      try {
        const response = await apiClient.get('/dashboard/stats');
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },

  // Campaigns
  campaigns: {
    getAll: async (params?: { limit?: number; offset?: number }) => {
      try {
        const response = await apiClient.get('/campaigns', { params });
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    getById: async (id: string) => {
      try {
        const response = await apiClient.get(`/campaigns/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    create: async (campaignData: any) => {
      try {
        const response = await apiClient.post('/campaigns', campaignData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    update: async (id: string, campaignData: any) => {
      try {
        const response = await apiClient.put(`/campaigns/${id}`, campaignData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    delete: async (id: string) => {
      try {
        const response = await apiClient.delete(`/campaigns/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },
  
  // Proposals
  proposals: {
    getAll: async (params?: { limit?: number; offset?: number }) => {
      try {
        const response = await apiClient.get('/proposals', { params });
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    getById: async (id: string) => {
      try {
        const response = await apiClient.get(`/proposals/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },
  
  // Email Templates
  emailTemplates: {
    getAll: async () => {
      try {
        const response = await apiClient.get('/email-templates');
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    getById: async (id: string) => {
      try {
        const response = await apiClient.get(`/email-templates/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    create: async (templateData: any) => {
      try {
        const response = await apiClient.post('/email-templates', templateData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    update: async (id: string, templateData: any) => {
      try {
        const response = await apiClient.put(`/email-templates/${id}`, templateData);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
    
    delete: async (id: string) => {
      try {
        const response = await apiClient.delete(`/email-templates/${id}`);
        return response.data;
      } catch (error) {
        throw normalizeError(error);
      }
    },
  },
};

export default apiService; 