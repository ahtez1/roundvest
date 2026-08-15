'use client';

import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from './api';

type User = {
	id: number;
	email: string;
	username: string;
	first_name: string;
	last_name: string;
};

type AuthContextType = {
	user: User | null;
	isLoading: boolean;
	login: (email: string, password: string) => Promise<{ success: boolean; msg?: string }>;
	register: (
		email: string,
		username: string,
		password: string
	) => Promise<{ success: boolean; msg?: string }>;
	logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
	const [user, setUser] = useState<User | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const router = useRouter();

	useEffect(() => {
		(async () => {
			const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
			if (token) {
				try {
					const res = await api.get('/api/auth/me/');
					setUser(res.data);
				} catch {
					localStorage.removeItem('accessToken');
					localStorage.removeItem('refreshToken');
				}
			}
			setIsLoading(false);
		})();
	}, []);

	const login = async (email: string, password: string) => {
		try {
			const res = await api.post('/api/auth/login/', { email, password });
			localStorage.setItem('accessToken', res.data.access);
			localStorage.setItem('refreshToken', res.data.refresh);
			const me = await api.get('/api/auth/me/');
			setUser(me.data);
			router.push('/dashboard');
			return { success: true };
		} catch (error: unknown) {
			return { success: false, msg: extractError(error) };
		}
	};

	const register = async (email: string, username: string, password: string) => {
		try {
			await api.post('/api/auth/register/', { email, username, password });
			return login(email, password);
		} catch (error: unknown) {
			return { success: false, msg: extractError(error) };
		}
	};

	const logout = () => {
		localStorage.removeItem('accessToken');
		localStorage.removeItem('refreshToken');
		setUser(null);
		router.push('/login');
	};

	return (
		<AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
			{children}
		</AuthContext.Provider>
	);
}

function extractError(error: unknown): string {
	if (typeof error === 'object' && error !== null && 'response' in error) {
		const response = (error as { response?: { data?: Record<string, unknown> } }).response;
		const data = response?.data;
		if (data) {
			const first = Object.values(data)[0];
			if (Array.isArray(first)) return String(first[0]);
			if (typeof first === 'string') return first;
		}
	}
	return 'Something went wrong. Please try again.';
}

export function useAuth() {
	const ctx = useContext(AuthContext);
	if (!ctx) throw new Error('useAuth must be used within AuthProvider');
	return ctx;
}
