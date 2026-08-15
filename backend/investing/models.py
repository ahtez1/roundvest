from django.conf import settings
from django.db import models

SYMBOL_CHOICES = [
    ("VOO", "Vanguard S&P 500 ETF"),
    ("VTI", "Vanguard Total Stock Market ETF"),
    ("QQQ", "Invesco QQQ Trust"),
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corp."),
    ("TSLA", "Tesla Inc."),
]


class UserInvestSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invest_settings"
    )
    symbol = models.CharField(max_length=10, choices=SYMBOL_CHOICES, default="VOO")

    def __str__(self):
        return f"{self.user.email} -> {self.symbol}"


class InvestmentOrder(models.Model):
    STATUS_CHOICES = [
        ("filled", "Filled"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investment_orders"
    )
    symbol = models.CharField(max_length=10)
    notional_amount = models.DecimalField(max_digits=10, decimal_places=2)
    filled_qty = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    filled_avg_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    alpaca_order_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} {self.symbol} ${self.notional_amount} ({self.status})"
