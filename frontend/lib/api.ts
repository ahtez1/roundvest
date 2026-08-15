import axios from 'axios';

const api = axios.create({
	baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
	headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
	if (typeof window !== 'undefined') {
		const token = localStorage.getItem('accessToken');
		if (token) {
			config.headers.Authorization = `Bearer ${token}`;
		}
	}
	return config;
});

// If a request 401s, try refreshing the access token once before giving up.
let refreshing: Promise<string | null> | null = null;

api.interceptors.response.use(
	(response) => response,
	async (error) => {
		const original = error.config;
		if (error.response?.status === 401 && !original._retry) {
			original._retry = true;
			const refreshToken =
				typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null;
			if (!refreshToken) {
				return Promise.reject(error);
			}
			try {
				if (!refreshing) {
					refreshing = axios
						.post(`${api.defaults.baseURL}/api/auth/refresh/`, { refresh: refreshToken })
						.then((res) => {
							localStorage.setItem('accessToken', res.data.access);
							return res.data.access as string;
						})
						.finally(() => {
							refreshing = null;
						});
				}
				const newToken = await refreshing;
				original.headers.Authorization = `Bearer ${newToken}`;
				return api(original);
			} catch {
				localStorage.removeItem('accessToken');
				localStorage.removeItem('refreshToken');
			}
		}
		return Promise.reject(error);
	}
);

export default api;
