'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { BankItem, Symbol, Transaction } from '@/lib/types';
import Navbar from '@/components/Navbar';
import PlaidLinkButton from '@/components/PlaidLinkButton';
import TransactionList from '@/components/TransactionList';
import RoundupSummaryCard from '@/components/RoundupSummaryCard';

export default function DashboardPage() {
	const { user, isLoading } = useAuth();
	const router = useRouter();

	const [bankItems, setBankItems] = useState<BankItem[]>([]);
	const [transactions, setTransactions] = useState<Transaction[]>([]);
	const [pendingBalance, setPendingBalance] = useState('0.00');
	const [symbols, setSymbols] = useState<Symbol[]>([]);
	const [selectedSymbol, setSelectedSymbol] = useState('VOO');
	const [syncing, setSyncing] = useState(false);
	const [investing, setInvesting] = useState(false);
	const [investMessage, setInvestMessage] = useState<string | null>(null);
	const [loadingData, setLoadingData] = useState(true);

	useEffect(() => {
		if (!isLoading && !user) router.push('/login');
	}, [isLoading, user, router]);

	const refreshData = useCallback(async () => {
		const [itemsRes, txRes, balRes, symRes, settingsRes] = await Promise.all([
			api.get('/api/banking/items/'),
			api.get('/api/roundups/transactions/'),
			api.get('/api/roundups/balance/'),
			api.get('/api/investing/symbols/'),
			api.get('/api/investing/settings/'),
		]);
		setBankItems(itemsRes.data);
		setTransactions(txRes.data);
		setPendingBalance(balRes.data.pending_roundup_balance);
		setSymbols(symRes.data);
		setSelectedSymbol(settingsRes.data.symbol);
		setLoadingData(false);
	}, []);

	useEffect(() => {
		if (!user) return;
		// Initial data load on mount/login - intentional one-shot fetch.
		// eslint-disable-next-line react-hooks/set-state-in-effect
		void refreshData();
	}, [user, refreshData]);

	const handleLinked = async () => {
		await refreshData();
		await handleSync();
	};

	const handleSync = async () => {
		setSyncing(true);
		try {
			await api.post('/api/banking/sync-transactions/');
			await refreshData();
		} finally {
			setSyncing(false);
		}
	};

	const handleInvestNow = async () => {
		setInvesting(true);
		setInvestMessage(null);
		try {
			const res = await api.post('/api/investing/invest-now/');
			setInvestMessage(
				`Bought ${res.data.filled_qty} shares of ${res.data.symbol} at $${res.data.filled_avg_price}.`
			);
			await refreshData();
		} catch (err: unknown) {
			const msg =
				(err as { response?: { data?: { error?: string } } }).response?.data?.error ||
				'Could not place order.';
			setInvestMessage(msg);
		} finally {
			setInvesting(false);
		}
	};

	const handleSymbolChange = async (symbol: string) => {
		setSelectedSymbol(symbol);
		await api.put('/api/investing/settings/', { symbol });
	};

	if (isLoading || !user) return null;

	return (
		<div className="flex flex-1 flex-col">
			<Navbar />
			<div className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
				{bankItems.length === 0 ? (
					<div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-12 text-center">
						<h2 className="mb-2 text-xl font-semibold text-zinc-900">Link a bank to get started</h2>
						<p className="mb-6 text-sm text-zinc-500">
							We&apos;ll pull in your recent transactions and round each one up to the nearest
							dollar.
						</p>
						<PlaidLinkButton onLinked={handleLinked} />
					</div>
				) : (
					<div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
						<div className="lg:col-span-2">
							<div className="mb-4 flex items-center justify-between">
								<h2 className="text-lg font-semibold text-zinc-900">Recent transactions</h2>
								<button
									onClick={handleSync}
									disabled={syncing}
									className="rounded-full border border-zinc-300 px-4 py-1.5 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 disabled:opacity-50"
								>
									{syncing ? 'Syncing...' : 'Sync transactions'}
								</button>
							</div>
							<div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
								{loadingData ? (
									<p className="py-8 text-center text-sm text-zinc-400">Loading...</p>
								) : (
									<TransactionList transactions={transactions} />
								)}
							</div>
						</div>

						<div className="flex flex-col gap-6">
							<RoundupSummaryCard
								pendingBalance={pendingBalance}
								symbol={selectedSymbol}
								onInvest={handleInvestNow}
								investing={investing}
								message={investMessage}
							/>

							<div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
								<div className="mb-3 text-sm font-medium text-zinc-500">Invest round-ups into</div>
								<select
									value={selectedSymbol}
									onChange={(e) => handleSymbolChange(e.target.value)}
									className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
								>
									{symbols.map((s) => (
										<option key={s.symbol} value={s.symbol}>
											{s.symbol} - {s.name}
										</option>
									))}
								</select>
							</div>
						</div>
					</div>
				)}
			</div>
		</div>
	);
}
