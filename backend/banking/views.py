from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from roundups.services import ingest_transactions

from .models import BankItem
from .plaid_client import get_plaid_client
from .serializers import BankItemSerializer


class LinkTokenView(APIView):
    """Returns a Plaid Link token, plus a `mode` flag telling the frontend
    whether this is a real Plaid Link token (drive the Plaid Link widget)
    or a fake one (skip the widget - it can't validate against Plaid's
    servers - and let the user "connect" a simulated sandbox bank directly).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = get_plaid_client()
        link_token = client.create_link_token(str(request.user.id))
        mode = "live" if (settings.PLAID_CLIENT_ID and settings.PLAID_SECRET) else "fake"
        return Response({"link_token": link_token, "mode": mode})


class ExchangePublicTokenView(APIView):
    """Exchanges a Plaid public_token for an access_token and stores it
    server-side. The access_token is never returned to the client."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        public_token = request.data.get("public_token")
        institution_name = request.data.get("institution_name", "Sandbox Bank")
        if not public_token:
            return Response({"error": "public_token is required"}, status=400)

        client = get_plaid_client()
        access_token, item_id = client.exchange_public_token(public_token)

        bank_item = BankItem.objects.create(
            user=request.user,
            access_token=access_token,
            item_id=item_id,
            institution_name=institution_name,
        )
        return Response(BankItemSerializer(bank_item).data, status=201)


class BankItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = BankItem.objects.filter(user=request.user)
        return Response(BankItemSerializer(items, many=True).data)


class SyncTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = get_plaid_client()
        total_new = 0
        for bank_item in BankItem.objects.filter(user=request.user):
            plaid_transactions = client.sync_transactions(bank_item.access_token)
            total_new += ingest_transactions(request.user, bank_item, plaid_transactions)
        return Response({"new_transactions": total_new})
