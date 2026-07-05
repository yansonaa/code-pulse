import axios, { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Commit APIs
export const commitApi = {
  uploadGitLog: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/commits/upload/git-log', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  uploadJson: (commits: unknown[]) => api.post('/commits/upload/json', commits),
  listCommits: (params?: Record<string, unknown>) => api.get('/commits/', { params }),
  getAuthors: () => api.get('/commits/authors'),
  getRepositories: () => api.get('/commits/repositories'),
  deleteAll: () => api.delete('/commits/all'),
};

// Stats APIs
export const statsApi = {
  getKPI: (params?: Record<string, unknown>) => api.get('/stats/kpi', { params }),
  getTrend: (params?: Record<string, unknown>) => api.get('/stats/trend', { params }),
  getCodeStats: (params?: Record<string, unknown>) => api.get('/stats/code', { params }),
  getHeatmap: (params?: Record<string, unknown>) => api.get('/stats/heatmap', { params }),
  getRadar: (params?: Record<string, unknown>) => api.get('/stats/radar', { params }),
  getAnomalies: (params?: Record<string, unknown>) => api.get('/stats/anomalies', { params }),
};

// Export APIs
export const exportApi = {
  exportCSV: (params?: Record<string, unknown>) => {
    return api.get('/export/csv', { params, responseType: 'blob' });
  },
  exportMemberCSV: (params?: Record<string, unknown>) => {
    return api.get('/export/members/csv', { params, responseType: 'blob' });
  },
};

// Mock APIs
export const mockApi = {
  generate: (days = 90, totalCommits = 2000) =>
    api.post(`/mock/generate?days=${days}&total_commits=${totalCommits}`),
  getDevelopers: () => api.get('/mock/developers'),
};

// Sync / Repository Config APIs
export const syncApi = {
  getConfigs: () => api.get('/sync/configs'),
  getConfig: (id: number) => api.get(`/sync/configs/${id}`),
  createConfig: (data: unknown) => api.post('/sync/configs', data),
  updateConfig: (id: number, data: unknown) => api.put(`/sync/configs/${id}`, data),
  deleteConfig: (id: number) => api.delete(`/sync/configs/${id}`),
  syncRepo: (id: number, days?: number, clearExisting?: boolean) =>
    api.post(`/sync/sync/${id}?days=${days || 90}&clear_existing=${clearExisting || false}`),
  syncAll: (days?: number) => api.post(`/sync/sync-all?days=${days || 90}`),
  getBranches: (path: string) => api.get(`/sync/branches?path=${encodeURIComponent(path)}`),
};

export default api;