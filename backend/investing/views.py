from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InvestmentOrder, UserInvestSettings
from .serializers import (
    InvestmentOrderSerializer,
    SymbolChoiceSerializer,
    UserInvestSettingsSerializer,
)
from .services import InvestError, get_portfolio, invest_pending_roundups


class SymbolListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(SymbolChoiceSerializer.all())


class InvestSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings_obj, _ = UserInvestSettings.objects.get_or_create(user=request.user)
        return Response(UserInvestSettingsSerializer(settings_obj).data)

    def put(self, request):
        settings_obj, _ = UserInvestSettings.objects.get_or_create(user=request.user)
        serializer = UserInvestSettingsSerializer(settings_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InvestNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order = invest_pending_roundups(request.user)
        except InvestError as e:
            return Response({"error": str(e)}, status=400)
        return Response(InvestmentOrderSerializer(order).data, status=201)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = InvestmentOrder.objects.filter(user=request.user)
        return Response(InvestmentOrderSerializer(orders, many=True).data)


class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_portfolio(request.user))
