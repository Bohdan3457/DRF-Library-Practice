from django.db import models
from borrowings.models import Borrowing


class Payment(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255, unique=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "pending"
        PAID = "PAID", "paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT", "payment"
        FINE = "FINE", "fine"

    status = models.CharField(max_length=7, choices=StatusChoices.choices)
    payment_type = models.CharField(
        max_length=7,
        choices=TypeChoices.choices,
        db_column="type",
    )

    def __str__(self):
        return f"{self.borrowing.book} - {self.session_id}"
