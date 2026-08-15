export function formatSignedCurrency(value: string): string {
	const n = parseFloat(value);
	const sign = n > 0 ? '+' : n < 0 ? '-' : '';
	return `${sign}$${Math.abs(n).toFixed(2)}`;
}

export type BankItem = {
	id: number;
	institution_name: string;
	created_at: string;
};

export type Transaction = {
	id: number;
	merchant_name: string;
	category: string;
	amount: string;
	date: string;
	roundup_entry: { roundup_amount: string; invested: boolean } | null;
};

export type Symbol = { symbol: string; name: string };

export type InvestmentOrder = {
	id: number;
	symbol: string;
	notional_amount: string;
	filled_qty: string | null;
	filled_avg_price: string | null;
	status: string;
	created_at: string;
};

export type Holding = {
	symbol: string;
	qty: string;
	cost_basis: string;
	current_price: string;
	current_value: string;
	gain_loss: string;
};

export type Portfolio = {
	holdings: Holding[];
	total_cost_basis: string;
	total_current_value: string;
	total_gain_loss: string;
};
