from rest_framework import serializers

from .models import SYMBOL_CHOICES, InvestmentOrder, UserInvestSettings


class InvestmentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOrder
        fields = [
            "id",
            "symbol",
            "notional_amount",
            "filled_qty",
            "filled_avg_price",
            "status",
            "created_at",
        ]


class UserInvestSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvestSettings
        fields = ["symbol"]


class SymbolChoiceSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    name = serializers.CharField()

    @staticmethod
    def all():
        return [{"symbol": s, "name": n} for s, n in SYMBOL_CHOICES]
