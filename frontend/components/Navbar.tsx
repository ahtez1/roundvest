'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function Navbar() {
	const { user, logout } = useAuth();
	const pathname = usePathname();

	const linkClass = (href: string) =>
		`rounded-full px-4 py-2 text-sm font-medium transition ${
			pathname === href
				? 'bg-emerald-600 text-white'
				: 'text-zinc-600 hover:bg-zinc-100'
		}`;

	return (
		<nav className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-4">
			<Link href="/dashboard" className="text-lg font-bold text-emerald-600">
				RoundVest
			</Link>
			<div className="flex items-center gap-2">
				<Link href="/dashboard" className={linkClass('/dashboard')}>
					Dashboard
				</Link>
				<Link href="/portfolio" className={linkClass('/portfolio')}>
					Portfolio
				</Link>
				{user && (
					<button
						onClick={logout}
						className="ml-2 rounded-full px-4 py-2 text-sm font-medium text-zinc-500 hover:bg-zinc-100"
					>
						Log out ({user.email})
					</button>
				)}
			</div>
		</nav>
	);
}
