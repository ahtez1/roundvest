from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from banking.models import BankItem

from .models import RoundupLedgerEntry, Transaction
from .roundup_math import calculate_roundup
from .services import ingest_transactions, pending_roundup_balance

User = get_user_model()


class RoundupMathTests(APITestCase):
    def test_rounds_up_to_next_dollar(self):
        self.assertEqual(calculate_roundup(Decimal("4.35")), Decimal("0.65"))
        self.assertEqual(calculate_roundup(Decimal("2.01")), Decimal("0.99"))
        self.assertEqual(calculate_roundup(Decimal("9.99")), Decimal("0.01"))

    def test_whole_dollar_amount_has_no_roundup(self):
        self.assertEqual(calculate_roundup(Decimal("5.00")), Decimal("0.00"))

    def test_zero_or_negative_amount_has_no_roundup(self):
        self.assertEqual(calculate_roundup(Decimal("0.00")), Decimal("0.00"))
        self.assertEqual(calculate_roundup(Decimal("-3.50")), Decimal("0.00"))


class FakeTxn:
    def __init__(self, transaction_id, amount):
        self.transaction_id = transaction_id
        self.merchant_name = "Test Merchant"
        self.amount = amount
        self.category = "GENERAL"
        from datetime import date

        self.date = date.today()


class IngestTransactionsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        self.bank_item = BankItem.objects.create(
            user=self.user, access_token="tok", item_id="item1"
        )

    def test_ingest_creates_transactions_and_roundup_entries(self):
        txns = [FakeTxn("t1", Decimal("4.35")), FakeTxn("t2", Decimal("2.00"))]
        created = ingest_transactions(self.user, self.bank_item, txns)

        self.assertEqual(created, 2)
        self.assertEqual(Transaction.objects.count(), 2)
        # $2.00 is a whole dollar amount -> no ledger entry generated
        self.assertEqual(RoundupLedgerEntry.objects.count(), 1)
        self.assertEqual(pending_roundup_balance(self.user), Decimal("0.65"))

    def test_ingest_is_idempotent(self):
        txns = [FakeTxn("t1", Decimal("4.35"))]
        ingest_transactions(self.user, self.bank_item, txns)
        created_again = ingest_transactions(self.user, self.bank_item, txns)

        self.assertEqual(created_again, 0)
        self.assertEqual(Transaction.objects.count(), 1)


class CrossUserIsolationTests(APITestCase):
    """Regression test for the IDOR class of bug found in the prior
    project, where endpoints trusted a client-supplied user id instead of
    scoping every query to request.user."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        self.user_b = User.objects.create_user(
            email="b@example.com", username="b", password="pw123456"
        )
        bank_item = BankItem.objects.create(
            user=self.user_a, access_token="tok", item_id="item-a"
        )
        ingest_transactions(self.user_a, bank_item, [FakeTxn("t1", Decimal("4.35"))])

    def test_user_cannot_see_another_users_transactions(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(reverse("transactions"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_user_cannot_see_another_users_roundup_balance(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(reverse("roundup-balance"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pending_roundup_balance"], "0.00")

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get(reverse("transactions"))
        self.assertEqual(response.status_code, 401)
