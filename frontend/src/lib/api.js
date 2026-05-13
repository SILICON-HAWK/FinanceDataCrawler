const API_BASE = 'http://localhost:8000/api';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || body.message || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  status: () => request('/status'),

  discover: {
    sectors: () =>
      request('/discover/sectors', { method: 'POST' }),
    companies: (timeout = 60) =>
      request('/discover/companies', { method: 'POST', body: JSON.stringify({ timeout }) }),
  },

  extract: {
    start: (body) =>
      request('/extract', { method: 'POST', body: JSON.stringify(body) }),
    status: () => request('/extract/status'),
  },

  companies: {
    list: (search = '') => request(`/companies${search ? `?search=${encodeURIComponent(search)}` : ''}`),
    get: (name) => request(`/companies/${encodeURIComponent(name)}`),
  },
};
