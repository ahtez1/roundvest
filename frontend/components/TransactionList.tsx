import { Transaction } from '@/lib/types';

export default function TransactionList({ transactions }: { transactions: Transaction[] }) {
	if (transactions.length === 0) {
		return <p className="py-8 text-center text-sm text-zinc-500">No transactions yet. Sync to pull in your latest purchases.</p>;
	}

	return (
		<div className="overflow-x-auto">
			<table className="w-full text-sm">
				<thead>
					<tr className="border-b border-zinc-200 text-left text-zinc-500">
						<th className="py-2 font-medium">Merchant</th>
						<th className="py-2 font-medium">Date</th>
						<th className="py-2 text-right font-medium">Amount</th>
						<th className="py-2 text-right font-medium">Round-up</th>
					</tr>
				</thead>
				<tbody>
					{transactions.map((t) => (
						<tr key={t.id} className="border-b border-zinc-100 last:border-0">
							<td className="py-2.5">
								<div className="font-medium text-zinc-900">{t.merchant_name}</div>
								<div className="text-xs text-zinc-400">{t.category}</div>
							</td>
							<td className="py-2.5 text-zinc-600">{t.date}</td>
							<td className="py-2.5 text-right text-zinc-900">${t.amount}</td>
							<td className="py-2.5 text-right">
								{t.roundup_entry ? (
									<span
										className={`rounded-full px-2 py-0.5 text-xs font-medium ${
											t.roundup_entry.invested
												? 'bg-zinc-100 text-zinc-500'
												: 'bg-emerald-100 text-emerald-700'
										}`}
									>
										+${t.roundup_entry.roundup_amount}
									</span>
								) : (
									<span className="text-xs text-zinc-300">-</span>
								)}
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}
