from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    cover = models.CharField(max_length=4, choices=CoverChoices.choices)

    def __str__(self) -> str:
        return f"{self.title}"
