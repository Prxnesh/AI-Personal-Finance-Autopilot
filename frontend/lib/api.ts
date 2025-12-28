import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth endpoints
export const authAPI = {
    register: (email: string, password: string) =>
        api.post('/auth/register', { email, password }),

    login: (email: string, password: string) =>
        api.post('/auth/login', { email, password }),

    getMe: () =>
        api.get('/auth/me'),
};

// Transaction endpoints
export const transactionAPI = {
    upload: (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/transactions/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    getAll: (limit = 100, offset = 0) =>
        api.get(`/transactions/?limit=${limit}&offset=${offset}`),

    updateCategory: (id: number, category: string) =>
        api.patch(`/transactions/${id}`, { category }),
};

// Dashboard endpoints
export const dashboardAPI = {
    getData: () => api.get('/dashboard/'),
};

// Insights endpoints
export const insightsAPI = {
    generate: () => api.post('/insights/generate'),
    getAll: () => api.get('/insights/'),
};

// Predictions endpoints
export const predictionsAPI = {
    generate: () => api.post('/predictions/generate'),
    getAll: () => api.get('/predictions/'),
};

// Recommendations endpoints
export const recommendationsAPI = {
    getAll: () => api.get('/recommendations/'),
};
