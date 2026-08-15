from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer
from .services import pending_roundup_balance


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)[:100]
        return Response(TransactionSerializer(transactions, many=True).data)


class RoundupBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"pending_roundup_balance": str(pending_roundup_balance(request.user))})
