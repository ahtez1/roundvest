from django.urls import path

from .views import (
    InvestNowView,
    InvestSettingsView,
    OrderHistoryView,
    PortfolioView,
    SymbolListView,
)

urlpatterns = [
    path("symbols/", SymbolListView.as_view(), name="symbols"),
    path("settings/", InvestSettingsView.as_view(), name="invest-settings"),
    path("invest-now/", InvestNowView.as_view(), name="invest-now"),
    path("orders/", OrderHistoryView.as_view(), name="orders"),
    path("portfolio/", PortfolioView.as_view(), name="portfolio"),
]
