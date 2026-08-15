"""Alpaca integration behind a small interface, with a real (paper trading)
and a fake (offline) implementation selected by whether ALPACA_API_KEY is
configured. See banking/plaid_client.py for the same pattern and rationale.

Note on multi-tenancy: Alpaca's regular (non-Broker) API gives you one
trading account tied to your API key pair, not one account per end user.
True per-user brokerage accounts require Alpaca's Broker API, which needs
business approval and is out of scope for a portfolio demo. Here, every
user's orders are placed against the same paper account, and each user's
"portfolio" is computed from *their own* InvestmentOrder rows rather than
the account's raw equity - so the numbers shown to a user are honestly
theirs, even though the underlying paper account is shared.
"""

import random
import time
import uuid
from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings

_FAKE_BASE_PRICES = {
    "VOO": Decimal("560.00"),
    "VTI": Decimal("305.00"),
    "QQQ": Decimal("515.00"),
    "AAPL": Decimal("232.00"),
    "MSFT": Decimal("430.00"),
    "TSLA": Decimal("260.00"),
}


@dataclass
class OrderResult:
    order_id: str
    status: str  # "filled" | "pending" | "failed"
    filled_qty: Decimal | None
    filled_avg_price: Decimal | None


class BaseAlpacaClient:
    def get_quote(self, symbol: str) -> Decimal:
        raise NotImplementedError

    def submit_notional_order(self, symbol: str, notional_amount: Decimal) -> OrderResult:
        raise NotImplementedError


class LiveAlpacaClient(BaseAlpacaClient):
    """Talks to the real Alpaca paper trading API."""

    def _trading_client(self):
        from alpaca.trading.client import TradingClient

        return TradingClient(
            settings.ALPACA_API_KEY, settings.ALPACA_API_SECRET, paper=True
        )

    def _data_client(self):
        from alpaca.data.historical import StockHistoricalDataClient

        return StockHistoricalDataClient(
            settings.ALPACA_API_KEY, settings.ALPACA_API_SECRET
        )

    def get_quote(self, symbol: str) -> Decimal:
        from alpaca.data.requests import StockLatestTradeRequest

        client = self._data_client()
        response = client.get_stock_latest_trade(
            StockLatestTradeRequest(symbol_or_symbols=symbol)
        )
        return Decimal(str(response[symbol].price))

    def submit_notional_order(self, symbol: str, notional_amount: Decimal) -> OrderResult:
        from alpaca.trading.enums import OrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest

        client = self._trading_client()
        order = client.submit_order(
            MarketOrderRequest(
                symbol=symbol,
                notional=float(notional_amount),
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
        )

        # Market orders during market hours usually fill within a second or
        # two; poll briefly so the UI can show a filled order right away.
        for _ in range(5):
            order = client.get_order_by_id(order.id)
            if order.status == "filled":
                break
            time.sleep(1)

        filled = order.status == "filled"
        return OrderResult(
            order_id=str(order.id),
            status="filled" if filled else "pending",
            filled_qty=Decimal(str(order.filled_qty)) if order.filled_qty else None,
            filled_avg_price=(
                Decimal(str(order.filled_avg_price)) if order.filled_avg_price else None
            ),
        )


class FakeAlpacaClient(BaseAlpacaClient):
    """Offline fake that fills every order instantly at a jittered price."""

    def get_quote(self, symbol: str) -> Decimal:
        base = _FAKE_BASE_PRICES.get(symbol, Decimal("100.00"))
        jitter = Decimal(str(round(random.uniform(-0.015, 0.015), 4)))
        price = base * (Decimal("1") + jitter)
        return price.quantize(Decimal("0.01"))

    def submit_notional_order(self, symbol: str, notional_amount: Decimal) -> OrderResult:
        price = self.get_quote(symbol)
        qty = (notional_amount / price).quantize(Decimal("0.00000001"))
        return OrderResult(
            order_id=f"fake-order-{uuid.uuid4().hex}",
            status="filled",
            filled_qty=qty,
            filled_avg_price=price,
        )


def get_alpaca_client() -> BaseAlpacaClient:
    if settings.ALPACA_API_KEY and settings.ALPACA_API_SECRET:
        return LiveAlpacaClient()
    return FakeAlpacaClient()
