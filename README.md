RoundVest
Round up your everyday purchases to the nearest dollar, and automatically invest the spare change in a real fractional-share brokerage order. An Acorns-style round-up investing app, built end to end: bank transaction sync, a round-up ledger, and brokerage order placement.

Backend: Django 6 + Django REST Framework, JWT auth
Frontend: Next.js (App Router) + TypeScript + Tailwind CSS
Bank data: Plaid Sandbox — real transaction sync
Investing: Alpaca Paper Trading — real fractional-share market orders, fake money
The app ships in fake mode by default: realistic simulated bank transactions and instantly-filled simulated brokerage orders, so it's fully demoable with zero external accounts. See Design notes for why, and Using the real Plaid/Alpaca sandboxes to switch it on.

Prerequisites
Python 3.11+ (built and tested on 3.13)
Node.js 18+ (built and tested on 22)
No database server, no Docker, no external accounts needed for the default demo mode
1. Get the code
git clone https://github.com/ahtez1/roundvest.git
cd roundvest
2. Start the backend
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults are fine for fake mode
python manage.py migrate
python manage.py runserver      # http://localhost:8000
Leave this running. In a new terminal, run the test suite to confirm everything's wired up correctly:

cd backend && source venv/bin/activate && python manage.py test
You should see Ran 14 tests ... OK.

3. Start the frontend
In another new terminal:

cd frontend
npm install
cp .env.local.example .env.local
npm run dev                     # http://localhost:3000
4. Walk through the app
Open http://localhost:3000 and:

Register an account (any email, username, password 8+ characters).
You're dropped on the dashboard. Since no Plaid/Alpaca keys are configured, it shows "Connect demo bank account" instead of the real Plaid widget.
Click it. This simulates linking a bank and immediately syncs a batch of realistic fake transactions (coffee shops, groceries, gas, etc.).
Each transaction shows its round-up next to it — e.g. a $54.99 charge rounds up $0.01, a $27.25 charge rounds up $0.75. Whole-dollar amounts round up nothing. The pending round-up balance card sums these.
Pick a symbol to invest in (VOO, VTI, QQQ, AAPL, MSFT, or TSLA) from the dropdown.
Click Invest now. Once the pending balance is at least $1.00, this places a (simulated) fractional-share market order for the full pending amount and resets the balance to $0.
Open the Portfolio tab to see your holdings, cost basis vs. current value, a gain/loss chart, and full order history.
Click Sync transactions again any time to pull in a fresh batch and repeat the cycle.
To sanity-check data isolation, log out and register a second account — it should start completely empty, with no visibility into the first account's data.

How it works
Link a bank — Plaid Link exchanges a public_token for an access_token, which is stored server-side only and never returned to the client (backend/banking/views.py).
Sync transactions — pulls the account's transaction history via Plaid's /transactions/sync, persists each one, and computes a round-up (ceil(amount) - amount) per transaction (backend/roundups/roundup_math.py, backend/roundups/services.py). Syncing is idempotent — re-syncing never double-counts a transaction.
Invest now — sums the user's pending (uninvested) round-up ledger entries and places one Alpaca notional market order for that dollar amount in the user's chosen symbol (backend/investing/services.py). The ledger entries that funded the order are marked invested.
Portfolio — computed per-user from that user's own InvestmentOrder history (shares bought × current market price), not from the underlying brokerage account's raw equity — see Design notes.
Using the real Plaid/Alpaca sandboxes (optional)
To prove out the live integrations instead of the fake fallback:

Sign up free at dashboard.plaid.com (Sandbox access is automatic) and alpaca.markets (create a Paper Trading API key pair).
Fill in backend/.env:
PLAID_CLIENT_ID=...
PLAID_SECRET=...          # use the Sandbox secret
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
Restart the backend (python manage.py runserver). No code changes or restarts needed on the frontend — it adapts automatically because the /api/banking/link-token/ response includes a mode field the UI reads.
On the dashboard, the button changes to "Link a bank account" and opens the real Plaid Link widget. Use Plaid's sandbox test credentials (username user_good, password pass_good) to link a fake-but-real institution.
Everything downstream — sync, round-ups, invest — now hits the real Plaid/Alpaca sandbox APIs instead of the fixtures. Orders are placed against your actual Alpaca paper account, so you can watch them show up in the Alpaca dashboard too.
Design notes
Dual-mode API clients. backend/banking/plaid_client.py and backend/investing/alpaca_client.py each define a small interface with a Live* implementation (talks to the real Plaid/Alpaca sandbox APIs) and a Fake* implementation (deterministic-ish realistic fixture data, no network calls). settings.py picks the live client automatically the moment PLAID_CLIENT_ID/PLAID_SECRET or ALPACA_API_KEY/ALPACA_API_SECRET are present in .env — no code changes needed. This is a real dependency-inversion pattern (not just a demo crutch): it's what makes the backend unit-testable without hitting external APIs, and what makes the whole app runnable by anyone who clones it with zero signups.

Why there's no per-user Alpaca account. Alpaca's standard (non-Broker) API gives you one trading account tied to one API key pair — not one account per end user. True per-user brokerage accounts require Alpaca's Broker API, which needs business approval and is out of scope for a portfolio project. Here, every user's orders are placed against the same paper account, and each user's "portfolio" is computed from their own InvestmentOrder rows rather than the account's raw equity — so the numbers shown to any given user are honestly theirs, even though the underlying paper account is shared. A production version would swap in the Broker API here without changing the rest of the architecture.

Security baseline. Every endpoint (other than register/login/refresh) requires JWT auth and scopes its queries to request.user — there's no client-supplied user ID anywhere. CORS_ALLOWED_ORIGINS is an explicit allowlist, never a wildcard. DEBUG defaults to False and is opt-in via .env. backend/roundups/tests.py, backend/banking/tests.py, and backend/investing/tests.py include regression tests asserting one user can never read another user's transactions, bank items, orders, or portfolio.

Project structure
backend/
  accounts/    email-based User, JWT register/login/refresh
  banking/     Plaid integration, BankItem model
  roundups/    Transaction + RoundupLedgerEntry, round-up math
  investing/   Alpaca integration, InvestmentOrder, portfolio calculation
frontend/
  app/         login, register, dashboard, portfolio pages (Next.js App Router)
  components/  PlaidLinkButton, TransactionList, RoundupSummaryCard, PortfolioChart
  lib/         api client (JWT + refresh), auth context, shared types
Troubleshooting
Static assets 403, or HMR websocket fails to connect in dev. Next.js's dev server blocks cross-origin requests to dev assets/HMR by default, and treats 127.0.0.1 and localhost as different origins even on the same machine. If you access the app via one and something (a proxy, a bookmark, a redirect) ends up loading it via the other, you'll see this. Both localhost and 127.0.0.1 are already allowlisted in frontend/next.config.ts via allowedDevOrigins — if you're hitting this from a different hostname (e.g. a LAN IP), add it there and restart the dev server (config changes aren't hot-reloaded).

Cannot connect to backend / network errors in the browser console. Confirm the backend is actually running on port 8000 and that frontend/.env.local's NEXT_PUBLIC_API_URL matches how you're accessing the frontend (both http://localhost:8000 and http://127.0.0.1:8000 work against the default backend config — just be consistent with whichever hostname you used for the frontend).

Login/register form submits but nothing happens. If you're actively editing frontend files while testing, Next's Fast Refresh remounts the page and silently resets in-progress form input. Reload the page fresh before testing after a save.

"Need at least $1.00 in pending round-ups to invest." Click Sync transactions a couple more times, or link the demo bank again — fake mode generates a new random batch of 8-14 transactions each sync.

Not built (deliberately, to keep this focused)
Docker / CI pipeline
Alpaca Broker API (true per-user brokerage accounts)
httpOnly-cookie token storage (currently localStorage, same pragmatic tradeoff as most SPA JWT setups — production hardening would move to httpOnly cookies + CSRF protection)
Scheduled/recurring round-up sweeps (currently manual "Invest now")
Deployment configs (Render/Vercel) — the app is deploy-ready (env-driven settings, no hardcoded hosts) but no specific platform config is included
