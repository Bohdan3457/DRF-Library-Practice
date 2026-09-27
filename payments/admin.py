from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "borrowing",
        "payment_type",
        "status",
        "money_to_pay",
        "session_id",
    )
    list_filter = ("status", "payment_type")
    search_fields = ("session_id",)
