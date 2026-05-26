import axios from 'axios';

const api = axios.create({ baseURL: '' });

api.interceptors.request.use((c) => {
  const t = localStorage.getItem('zb_token');
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401) {
      localStorage.removeItem('zb_token');
      if (location.pathname !== '/login') location.href = '/login';
    }
    return Promise.reject(e);
  },
);

export default api;
