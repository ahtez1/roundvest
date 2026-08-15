from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from banking.models import BankItem
from roundups.services import ingest_transactions
from roundups.tests import FakeTxn

from .models import InvestmentOrder
from .services import InvestError, invest_pending_roundups

User = get_user_model()


class InvestPendingRoundupsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        bank_item = BankItem.objects.create(
            user=self.user, access_token="tok", item_id="item1"
        )
        ingest_transactions(self.user, bank_item, [FakeTxn("t1", Decimal("4.35"))])

    def test_raises_when_balance_below_minimum(self):
        with self.assertRaises(InvestError):
            invest_pending_roundups(self.user)

    def test_invests_full_pending_balance_and_marks_entries_invested(self):
        bank_item = self.user.bank_items.first()
        ingest_transactions(
            self.user,
            bank_item,
            [FakeTxn("t2", Decimal("3.00")), FakeTxn("t3", Decimal("2.10"))],
        )
        # pending: 0.65 + 0.90 = 1.55 -> above the $1 minimum

        order = invest_pending_roundups(self.user)

        self.assertEqual(order.status, "filled")
        self.assertEqual(order.notional_amount, Decimal("1.55"))
        self.assertTrue(
            self.user.roundup_entries.filter(invested=False).count() == 0
        )


class PortfolioCrossUserIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        self.user_b = User.objects.create_user(
            email="b@example.com", username="b", password="pw123456"
        )
        InvestmentOrder.objects.create(
            user=self.user_a,
            symbol="VOO",
            notional_amount=Decimal("10.00"),
            filled_qty=Decimal("0.02"),
            filled_avg_price=Decimal("500.00"),
            status="filled",
        )

    def test_user_only_sees_their_own_orders(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(reverse("orders"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_user_only_sees_their_own_portfolio_holdings(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(reverse("portfolio"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["holdings"], [])
        self.assertEqual(response.data["total_cost_basis"], "0")
