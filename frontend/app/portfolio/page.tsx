'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { InvestmentOrder, Portfolio, formatSignedCurrency } from '@/lib/types';
import Navbar from '@/components/Navbar';
import PortfolioChart from '@/components/PortfolioChart';

export default function PortfolioPage() {
	const { user, isLoading } = useAuth();
	const router = useRouter();
	const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
	const [orders, setOrders] = useState<InvestmentOrder[]>([]);
	const [loadingData, setLoadingData] = useState(true);

	useEffect(() => {
		if (!isLoading && !user) router.push('/login');
	}, [isLoading, user, router]);

	useEffect(() => {
		if (!user) return;
		Promise.all([api.get('/api/investing/portfolio/'), api.get('/api/investing/orders/')]).then(
			([portfolioRes, ordersRes]) => {
				setPortfolio(portfolioRes.data);
				setOrders(ordersRes.data);
				setLoadingData(false);
			}
		);
	}, [user]);

	if (isLoading || !user) return null;

	const gainLoss = portfolio ? parseFloat(portfolio.total_gain_loss) : 0;

	return (
		<div className="flex flex-1 flex-col">
			<Navbar />
			<div className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
				{loadingData ? (
					<p className="py-8 text-center text-sm text-zinc-400">Loading...</p>
				) : !portfolio || portfolio.holdings.length === 0 ? (
					<div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-12 text-center">
						<h2 className="mb-2 text-xl font-semibold text-zinc-900">No investments yet</h2>
						<p className="text-sm text-zinc-500">
							Sync some transactions and invest your round-ups from the dashboard to see your
							portfolio here.
						</p>
					</div>
				) : (
					<>
						<div className="mb-6 grid grid-cols-3 gap-4">
							<div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
								<div className="text-sm font-medium text-zinc-500">Invested</div>
								<div className="mt-1 text-2xl font-bold text-zinc-900">
									${portfolio.total_cost_basis}
								</div>
							</div>
							<div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
								<div className="text-sm font-medium text-zinc-500">Current value</div>
								<div className="mt-1 text-2xl font-bold text-zinc-900">
									${portfolio.total_current_value}
								</div>
							</div>
							<div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
								<div className="text-sm font-medium text-zinc-500">Gain / loss</div>
								<div
									className={`mt-1 text-2xl font-bold ${
										gainLoss >= 0 ? 'text-emerald-600' : 'text-red-600'
									}`}
								>
									{formatSignedCurrency(portfolio.total_gain_loss)}
								</div>
							</div>
						</div>

						<div className="mb-6 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
							<h2 className="mb-4 text-lg font-semibold text-zinc-900">Holdings</h2>
							<PortfolioChart holdings={portfolio.holdings} />
						</div>

						<div className="mb-6 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
							<table className="w-full text-sm">
								<thead>
									<tr className="border-b border-zinc-200 text-left text-zinc-500">
										<th className="py-2 font-medium">Symbol</th>
										<th className="py-2 text-right font-medium">Shares</th>
										<th className="py-2 text-right font-medium">Cost basis</th>
										<th className="py-2 text-right font-medium">Current value</th>
										<th className="py-2 text-right font-medium">Gain / loss</th>
									</tr>
								</thead>
								<tbody>
									{portfolio.holdings.map((h) => (
										<tr key={h.symbol} className="border-b border-zinc-100 last:border-0">
											<td className="py-2.5 font-medium text-zinc-900">{h.symbol}</td>
											<td className="py-2.5 text-right text-zinc-600">{h.qty}</td>
											<td className="py-2.5 text-right text-zinc-600">${h.cost_basis}</td>
											<td className="py-2.5 text-right text-zinc-900">${h.current_value}</td>
											<td
												className={`py-2.5 text-right font-medium ${
													parseFloat(h.gain_loss) >= 0 ? 'text-emerald-600' : 'text-red-600'
												}`}
											>
												{formatSignedCurrency(h.gain_loss)}
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>

						<div className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
							<h2 className="mb-2 px-2 text-lg font-semibold text-zinc-900">Order history</h2>
							<table className="w-full text-sm">
								<thead>
									<tr className="border-b border-zinc-200 text-left text-zinc-500">
										<th className="py-2 font-medium">Date</th>
										<th className="py-2 font-medium">Symbol</th>
										<th className="py-2 text-right font-medium">Amount</th>
										<th className="py-2 text-right font-medium">Shares</th>
										<th className="py-2 text-right font-medium">Status</th>
									</tr>
								</thead>
								<tbody>
									{orders.map((o) => (
										<tr key={o.id} className="border-b border-zinc-100 last:border-0">
											<td className="py-2.5 text-zinc-600">
												{new Date(o.created_at).toLocaleDateString()}
											</td>
											<td className="py-2.5 font-medium text-zinc-900">{o.symbol}</td>
											<td className="py-2.5 text-right text-zinc-600">${o.notional_amount}</td>
											<td className="py-2.5 text-right text-zinc-600">{o.filled_qty ?? '-'}</td>
											<td className="py-2.5 text-right">
												<span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
													{o.status}
												</span>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</>
				)}
			</div>
		</div>
	);
}
