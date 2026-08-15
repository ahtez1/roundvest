from rest_framework import serializers

from .models import RoundupLedgerEntry, Transaction


class RoundupLedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundupLedgerEntry
        fields = ["roundup_amount", "invested"]


class TransactionSerializer(serializers.ModelSerializer):
    roundup_entry = RoundupLedgerEntrySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "merchant_name",
            "category",
            "amount",
            "date",
            "roundup_entry",
        ]
