from django.urls import path

from .views import (
    BankItemListView,
    ExchangePublicTokenView,
    LinkTokenView,
    SyncTransactionsView,
)

urlpatterns = [
    path("link-token/", LinkTokenView.as_view(), name="link-token"),
    path("exchange-public-token/", ExchangePublicTokenView.as_view(), name="exchange-public-token"),
    path("items/", BankItemListView.as_view(), name="bank-items"),
    path("sync-transactions/", SyncTransactionsView.as_view(), name="sync-transactions"),
]
