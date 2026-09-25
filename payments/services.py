import stripe
from borrowings.models import Borrowing
from library_service import settings


def create_stripe_session(borrowing: Borrowing):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    borrow_days = (
        borrowing.expected_return_date - borrowing.borrow_date
    ).days
    price_per_day = borrowing.book.daily_fee
    sum_to_pay = 100 * (borrow_days * price_per_day)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "uah",
                    "product_data": {
                        "name": f"Borrowing book: {borrowing.book.title}",
                    },
                    "unit_amount": int(sum_to_pay),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=(
            "http://127.0.0.1:8000/api/payments/success/"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url="http://127.0.0.1:8000/api/payments/cancel/",
    )
    return session.url, session.id, sum_to_pay / 100
