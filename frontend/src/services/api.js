import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;

  // Let axios/browser set Content-Type with boundary for FormData
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const login = (username, password) => {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
};
export const getMe = () => api.get('/auth/me');

// Upload — unified endpoint
// Question Papers: medium + class_level (subjects auto-detected)
// LO Mappings: subject + class_level (auto-detected from header)
export const uploadFiles = (files, { medium, classLevel, subject, uploadType }) => {
  const fd = new FormData();
  files.forEach(f => fd.append('files', f));
  fd.append('medium', medium || '');
  fd.append('class_level', String(classLevel || '0'));
  fd.append('subject', subject || '');
  fd.append('upload_type', uploadType || 'auto');
  return api.post('/upload/files', fd);
};

// Legacy upload endpoints
export const uploadQuestionPaper = (file, medium, classLevel) => {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('medium', medium || '');
  fd.append('class_level', String(classLevel || '0'));
  return api.post('/upload/question-paper', fd);
};
export const uploadLOMapping = (file, subject, classLevel) => {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('subject', subject || '');
  fd.append('class_level', String(classLevel || '0'));
  return api.post('/upload/lo-mapping', fd);
};

export const getUploadedFiles = () => api.get('/upload/list');
export const deleteUploadedFile = (id) => api.delete(`/upload/files/${id}`);
export const clearAllUploads = () => api.delete('/upload/clear');

// Parse
// Question paper: auto-detects class, medium, subjects from PDF header
export const parseQuestionPaper = (fileId, medium, classLevel) =>
  api.post(`/parse/question-paper/${fileId}?medium=${encodeURIComponent(medium || '')}&class_level=${classLevel || 0}`);

// LO mapping: auto-detects subject and class from PDF header
export const parseLOMapping = (fileId, subject, classLevel) =>
  api.post(`/parse/lo-mapping/${fileId}?subject=${encodeURIComponent(subject || '')}&class_level=${classLevel || 0}`);

// Resolve: merges ALL parsed questions with ALL parsed LOs
export const resolveMappings = (medium) =>
  api.post(`/parse/resolve-mappings?medium=${encodeURIComponent(medium || '')}`);

export const getParsedQuestions = () => api.get('/parse/questions');
export const getParsedLOMappings = () => api.get('/parse/lo-mappings');
export const getMergedData = () => api.get('/parse/merged');
export const getParseSummary = () => api.get('/parse/summary');

// Validate
export const runValidation = (languages) => api.post(`/validate/run?languages=${encodeURIComponent(languages)}`);
export const getValidationReport = () => api.get('/validate/report');
export const getValidationSummary = () => api.get('/validate/summary');
export const exportValidationReport = () => api.get('/validate/export-report');

// Export
export const generateDumpSheet = (params) => {
  const q = new URLSearchParams(params).toString();
  return api.post(`/export/generate?${q}`);
};
export const exportToExcel = (filename, languages, applyValidation) =>
  api.post(`/export/excel?filename=${encodeURIComponent(filename)}&languages=${encodeURIComponent(languages)}&apply_validation=${applyValidation}`);
export const getOutputFiles = () => api.get('/export/files');
export const getExportHistory = () => api.get('/export/history');
export const createMediaZip = () => api.post('/export/media-zip');
export const createBundle = (dump, media, validation) =>
  api.post(`/export/bundle?include_dump=${dump}&include_media=${media}&include_validation=${validation}`);
export const clearExport = () => api.post('/export/clear');

// Media
export const getMediaFiles = () => api.get('/media/files');
export const getMediaStats = () => api.get('/media/stats');
export const deleteMediaFile = (cat, name) => api.delete(`/media/files/${cat}/${name}`);
export const clearAllMedia = () => api.delete('/media/clear');
export const validateMediaPaths = () => api.get('/media/validate-paths');

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats');

export default api;
