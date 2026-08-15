"""Plaid integration behind a small interface, with a real (sandbox) and a
fake (offline) implementation selected by settings.PLAID_MODE.

This exists so the app is fully runnable and demoable with zero external
signups (fake mode is the default), while the real Plaid sandbox wiring is
a complete, working implementation that activates the moment API keys are
present in .env.
"""

import random
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings


@dataclass
class PlaidTransaction:
    transaction_id: str
    merchant_name: str
    amount: Decimal  # positive = money out of the account
    date: date
    category: str


class BasePlaidClient:
    def create_link_token(self, user_id: str) -> str:
        raise NotImplementedError

    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        """Returns (access_token, item_id)."""
        raise NotImplementedError

    def sync_transactions(self, access_token: str) -> list[PlaidTransaction]:
        raise NotImplementedError


class LivePlaidClient(BasePlaidClient):
    """Talks to the real Plaid Sandbox API."""

    def _client(self):
        from plaid.api import plaid_api
        from plaid.api_client import ApiClient
        from plaid.configuration import Configuration, Environment

        configuration = Configuration(
            host=Environment.Sandbox,
            api_key={
                "clientId": settings.PLAID_CLIENT_ID,
                "secret": settings.PLAID_SECRET,
            },
        )
        return plaid_api.PlaidApi(ApiClient(configuration))

    def create_link_token(self, user_id: str) -> str:
        from plaid.model.country_code import CountryCode
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import (
            LinkTokenCreateRequestUser,
        )
        from plaid.model.products import Products

        client = self._client()
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="RoundVest",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(request)
        return response["link_token"]

    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        from plaid.model.item_public_token_exchange_request import (
            ItemPublicTokenExchangeRequest,
        )

        client = self._client()
        response = client.item_public_token_exchange(
            ItemPublicTokenExchangeRequest(public_token=public_token)
        )
        return response["access_token"], response["item_id"]

    def sync_transactions(self, access_token: str) -> list[PlaidTransaction]:
        from plaid.model.transactions_sync_request import TransactionsSyncRequest

        client = self._client()
        added: list[PlaidTransaction] = []
        cursor = None
        has_more = True
        while has_more:
            request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
            if cursor is None:
                del request.cursor
            response = client.transactions_sync(request)
            for txn in response["added"]:
                if txn["amount"] <= 0:
                    continue  # only spend, not refunds/deposits
                added.append(
                    PlaidTransaction(
                        transaction_id=txn["transaction_id"],
                        merchant_name=txn.get("merchant_name") or txn["name"],
                        amount=Decimal(str(txn["amount"])),
                        date=txn["date"],
                        category=(txn.get("personal_finance_category") or {}).get(
                            "primary", "GENERAL"
                        ),
                    )
                )
            cursor = response["next_cursor"]
            has_more = response["has_more"]
        return added


_FAKE_MERCHANTS = [
    ("Blue Bottle Coffee", "FOOD_AND_DRINK"),
    ("Trader Joe's", "GROCERIES"),
    ("Shell Gas Station", "TRANSPORTATION"),
    ("Uber", "TRANSPORTATION"),
    ("Netflix", "ENTERTAINMENT"),
    ("Chipotle", "FOOD_AND_DRINK"),
    ("Target", "SHOPPING"),
    ("Amazon", "SHOPPING"),
    ("Whole Foods", "GROCERIES"),
    ("Spotify", "ENTERTAINMENT"),
]


class FakePlaidClient(BasePlaidClient):
    """Offline, deterministic-ish fake with realistic looking data so the
    app can be cloned and demoed with no Plaid account."""

    def create_link_token(self, user_id: str) -> str:
        return f"fake-link-token-{uuid.uuid4().hex[:12]}"

    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        return f"fake-access-{uuid.uuid4().hex}", f"fake-item-{uuid.uuid4().hex[:16]}"

    def sync_transactions(self, access_token: str) -> list[PlaidTransaction]:
        rng = random.Random(access_token)  # stable per bank item, still varied
        count = rng.randint(8, 14)
        transactions = []
        for i in range(count):
            merchant, category = rng.choice(_FAKE_MERCHANTS)
            dollars = rng.randint(2, 65)
            cents = rng.choice([5, 15, 20, 25, 40, 49, 50, 65, 75, 89, 99, 0])
            amount = Decimal(f"{dollars}.{cents:02d}")
            transactions.append(
                PlaidTransaction(
                    transaction_id=f"fake-txn-{access_token[:8]}-{i}-{uuid.uuid4().hex[:6]}",
                    merchant_name=merchant,
                    amount=amount,
                    date=date.today() - timedelta(days=rng.randint(0, 13)),
                    category=category,
                )
            )
        return transactions


def get_plaid_client() -> BasePlaidClient:
    if settings.PLAID_CLIENT_ID and settings.PLAID_SECRET:
        return LivePlaidClient()
    return FakePlaidClient()
