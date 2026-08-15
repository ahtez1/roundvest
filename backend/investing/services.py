from decimal import Decimal

from django.db import transaction as db_transaction

from roundups.models import RoundupLedgerEntry
from roundups.services import pending_roundup_balance

from .alpaca_client import get_alpaca_client
from .models import InvestmentOrder, UserInvestSettings

MIN_INVEST_AMOUNT = Decimal("1.00")


class InvestError(Exception):
    pass


def invest_pending_roundups(user):
    amount = pending_roundup_balance(user)
    if amount < MIN_INVEST_AMOUNT:
        raise InvestError(
            f"Need at least ${MIN_INVEST_AMOUNT} in pending round-ups to invest "
            f"(you have ${amount})."
        )

    settings_obj, _ = UserInvestSettings.objects.get_or_create(user=user)
    symbol = settings_obj.symbol

    client = get_alpaca_client()
    result = client.submit_notional_order(symbol, amount)

    with db_transaction.atomic():
        order = InvestmentOrder.objects.create(
            user=user,
            symbol=symbol,
            notional_amount=amount,
            filled_qty=result.filled_qty,
            filled_avg_price=result.filled_avg_price,
            alpaca_order_id=result.order_id,
            status=result.status,
        )
        entries = RoundupLedgerEntry.objects.select_for_update().filter(
            user=user, invested=False
        )
        entries.update(invested=True, investment_order=order)

    return order


def get_portfolio(user):
    client = get_alpaca_client()
    orders = InvestmentOrder.objects.filter(user=user, status="filled")

    by_symbol: dict[str, dict] = {}
    for order in orders:
        entry = by_symbol.setdefault(
            order.symbol, {"symbol": order.symbol, "qty": Decimal("0"), "cost_basis": Decimal("0")}
        )
        entry["qty"] += order.filled_qty or Decimal("0")
        entry["cost_basis"] += order.notional_amount

    holdings = []
    total_cost_basis = Decimal("0")
    total_current_value = Decimal("0")
    for symbol, data in by_symbol.items():
        price = client.get_quote(symbol)
        current_value = (data["qty"] * price).quantize(Decimal("0.01"))
        holdings.append(
            {
                "symbol": symbol,
                "qty": str(data["qty"]),
                "cost_basis": str(data["cost_basis"]),
                "current_price": str(price),
                "current_value": str(current_value),
                "gain_loss": str(current_value - data["cost_basis"]),
            }
        )
        total_cost_basis += data["cost_basis"]
        total_current_value += current_value

    return {
        "holdings": holdings,
        "total_cost_basis": str(total_cost_basis),
        "total_current_value": str(total_current_value),
        "total_gain_loss": str(total_current_value - total_cost_basis),
    }
