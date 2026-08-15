from django.conf import settings
from django.db import models


class BankItem(models.Model):
    """A linked bank connection. access_token never leaves the server."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_items"
    )
    access_token = models.CharField(max_length=255)
    item_id = models.CharField(max_length=255, unique=True)
    institution_name = models.CharField(max_length=255, default="Sandbox Bank")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.institution_name}"
