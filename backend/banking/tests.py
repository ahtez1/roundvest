from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import BankItem

User = get_user_model()


class ExchangePublicTokenTests(APITestCase):
    """Regression test: the old project's Plaid exchange endpoint returned
    the raw access_token to the client. This one must never do that."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        self.client.force_authenticate(user=self.user)

    def test_exchange_does_not_leak_access_token(self):
        response = self.client.post(
            reverse("exchange-public-token"),
            {"public_token": "fake-public-token", "institution_name": "Test Bank"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("access_token", response.data)
        self.assertEqual(BankItem.objects.get().access_token != "", True)


class BankItemCrossUserIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="a@example.com", username="a", password="pw123456"
        )
        self.user_b = User.objects.create_user(
            email="b@example.com", username="b", password="pw123456"
        )
        BankItem.objects.create(user=self.user_a, access_token="tok", item_id="item-a")

    def test_user_only_sees_their_own_bank_items(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(reverse("bank-items"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
