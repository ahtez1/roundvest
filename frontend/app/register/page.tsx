'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useAuth } from '@/lib/auth';

export default function RegisterPage() {
	const { register } = useAuth();
	const [email, setEmail] = useState('');
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	const [busy, setBusy] = useState(false);

	const handleSubmit = async (e: FormEvent) => {
		e.preventDefault();
		setError('');
		setBusy(true);
		const res = await register(email, username, password);
		setBusy(false);
		if (!res.success) setError(res.msg || 'Registration failed');
	};

	return (
		<div className="flex flex-1 items-center justify-center px-6">
			<form onSubmit={handleSubmit} className="w-full max-w-sm rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm">
				<h1 className="mb-6 text-2xl font-bold text-zinc-900">Create your account</h1>
				{error && (
					<div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
				)}
				<label className="mb-1 block text-sm font-medium text-zinc-700">Email</label>
				<input
					type="email"
					required
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					className="mb-4 w-full rounded-lg border border-zinc-300 px-3 py-2 focus:border-emerald-500 focus:outline-none"
				/>
				<label className="mb-1 block text-sm font-medium text-zinc-700">Username</label>
				<input
					type="text"
					required
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					className="mb-4 w-full rounded-lg border border-zinc-300 px-3 py-2 focus:border-emerald-500 focus:outline-none"
				/>
				<label className="mb-1 block text-sm font-medium text-zinc-700">Password</label>
				<input
					type="password"
					required
					minLength={8}
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					className="mb-6 w-full rounded-lg border border-zinc-300 px-3 py-2 focus:border-emerald-500 focus:outline-none"
				/>
				<button
					type="submit"
					disabled={busy}
					className="w-full rounded-full bg-emerald-600 py-2.5 font-medium text-white transition hover:bg-emerald-700 disabled:opacity-50"
				>
					{busy ? 'Creating account...' : 'Create account'}
				</button>
				<p className="mt-4 text-center text-sm text-zinc-600">
					Already have an account?{' '}
					<Link href="/login" className="font-medium text-emerald-600">
						Log in
					</Link>
				</p>
			</form>
		</div>
	);
}
