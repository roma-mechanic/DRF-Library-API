from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    payment_success_view,
    payment_failed_view,
    # PurchaseView,
)

app_name = "payment"
router = routers.DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls), name="payment"),
    path("success/", payment_success_view, name="success"),
    path("failed/", payment_failed_view, name="failed"),
]
