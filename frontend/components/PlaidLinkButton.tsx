'use client';

import { useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import api from '@/lib/api';

export default function PlaidLinkButton({ onLinked }: { onLinked: () => void }) {
	const [linkToken, setLinkToken] = useState<string | null>(null);
	const [mode, setMode] = useState<'live' | 'fake' | null>(null);
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		api.get('/api/banking/link-token/').then((res) => {
			setLinkToken(res.data.link_token);
			setMode(res.data.mode);
		});
	}, []);

	const { open, ready } = usePlaidLink({
		token: mode === 'live' ? (linkToken ?? '') : '',
		onSuccess: async (public_token, metadata) => {
			if (!public_token) return;
			await exchangeToken(public_token, metadata.institution?.name ?? 'Sandbox Bank');
		},
	});

	const exchangeToken = async (publicToken: string, institutionName: string) => {
		setBusy(true);
		try {
			await api.post('/api/banking/exchange-public-token/', {
				public_token: publicToken,
				institution_name: institutionName,
			});
			onLinked();
		} finally {
			setBusy(false);
		}
	};

	// Fake mode: there's no real Plaid Link token to hand the Plaid widget,
	// so simulate the "user picked a bank and consented" step directly.
	const handleClick = () => {
		if (mode === 'fake') {
			exchangeToken('fake-public-token', 'Sandbox Bank (Demo Mode)');
		} else {
			open();
		}
	};

	const disabled = !mode || (mode === 'live' && (!ready || !linkToken)) || busy;

	return (
		<button
			onClick={handleClick}
			disabled={disabled}
			className="rounded-full bg-emerald-600 px-5 py-2.5 font-medium text-white transition hover:bg-emerald-700 disabled:opacity-50"
		>
			{busy ? 'Linking...' : mode === 'fake' ? 'Connect demo bank account' : 'Link a bank account'}
		</button>
	);
}
