from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/banking/", include("banking.urls")),
    path("api/roundups/", include("roundups.urls")),
    path("api/investing/", include("investing.urls")),
]
