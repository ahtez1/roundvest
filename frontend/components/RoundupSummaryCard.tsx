export default function RoundupSummaryCard({
	pendingBalance,
	symbol,
	onInvest,
	investing,
	message,
}: {
	pendingBalance: string;
	symbol: string;
	onInvest: () => void;
	investing: boolean;
	message: string | null;
}) {
	const amount = parseFloat(pendingBalance || '0');

	return (
		<div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
			<div className="text-sm font-medium text-zinc-500">Pending round-ups</div>
			<div className="mt-1 text-4xl font-bold text-zinc-900">${pendingBalance}</div>
			<p className="mt-2 text-sm text-zinc-500">
				Ready to invest in <span className="font-medium text-zinc-700">{symbol}</span> once you hit
				the $1.00 minimum.
			</p>
			<button
				onClick={onInvest}
				disabled={investing || amount < 1}
				className="mt-4 w-full rounded-full bg-emerald-600 py-2.5 font-medium text-white transition hover:bg-emerald-700 disabled:opacity-40"
			>
				{investing ? 'Placing order...' : 'Invest now'}
			</button>
			{message && <p className="mt-3 text-center text-sm text-zinc-600">{message}</p>}
		</div>
	);
}
