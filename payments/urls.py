from rest_framework.routers import DefaultRouter
from payments.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView
)
from rest_framework.urls import path


router = DefaultRouter()

router.register("payments", PaymentViewSet)

urlpatterns = [
    path(
        "success/",
        PaymentSuccessView.as_view(),
        name="payment-success"
    ),
    path(
        "cancel/",
        PaymentCancelView.as_view(),
        name="payment-cancel"
    ),
] + router.urls


app_name = "payments"
