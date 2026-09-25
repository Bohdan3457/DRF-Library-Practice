from django.utils import timezone
from borrowings.models import Borrowing
from borrowings.telegram_services import send_telegram_notification


def check_overdue_borrowings():
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True
    ).select_related("book", "user")

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue borrowing alert!\n"
                f"Book: {borrowing.book.title}\n"
                f"User: {borrowing.user.email}\n"
                f"Expected return date: {borrowing.expected_return_date}"
            )
            send_telegram_notification(message)
    else:
        send_telegram_notification("No borrowings overdue today!")
