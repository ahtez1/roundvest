from django.urls import path

from .views import RoundupBalanceView, TransactionListView

urlpatterns = [
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("balance/", RoundupBalanceView.as_view(), name="roundup-balance"),
]
