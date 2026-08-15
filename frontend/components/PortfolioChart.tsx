'use client';

import {
	Bar,
	BarChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from 'recharts';
import { Holding } from '@/lib/types';

export default function PortfolioChart({ holdings }: { holdings: Holding[] }) {
	const data = holdings.map((h) => ({
		symbol: h.symbol,
		'Cost basis': parseFloat(h.cost_basis),
		'Current value': parseFloat(h.current_value),
	}));

	return (
		<ResponsiveContainer width="100%" height={280}>
			<BarChart data={data}>
				<CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
				<XAxis dataKey="symbol" stroke="#71717a" fontSize={12} />
				<YAxis stroke="#71717a" fontSize={12} tickFormatter={(v) => `$${v}`} />
				<Tooltip formatter={(value) => `$${Number(value ?? 0).toFixed(2)}`} />
				<Legend />
				<Bar dataKey="Cost basis" fill="#a1a1aa" radius={[4, 4, 0, 0]} />
				<Bar dataKey="Current value" fill="#059669" radius={[4, 4, 0, 0]} />
			</BarChart>
		</ResponsiveContainer>
	);
}
