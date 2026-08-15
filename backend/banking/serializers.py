from rest_framework import serializers

from .models import BankItem


class BankItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankItem
        fields = ["id", "institution_name", "created_at"]
