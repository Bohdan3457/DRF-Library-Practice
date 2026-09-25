import stripe
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from library_service import settings
from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(borrowing__user=user)
        else:
            user_id = self.request.query_params.get("user")
            if user_id:
                queryset = queryset.filter(borrowing__user_id=user_id)

        return queryset.select_related(
            "borrowing",
            "borrowing__book",
            "borrowing__user",
        )


class PaymentSuccessView(APIView):
    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID is missing"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment = Payment.objects.get(session_id=session_id)
                payment.status = Payment.StatusChoices.PAID
                payment.save()

                return Response(
                    {"message": "Payment was successful! Thank you."},
                    status=status.HTTP_200_OK
                )

            else:
                return Response(
                    {"message": "Payment is not completed yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment with this session_id not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCancelView(APIView):
    def get(self, request):
        message = (
            "Payment was cancelled. "
            "You can try again later "
            "(session is active for 24 hours)."
        )
        return Response(
            {"message": message},
            status=status.HTTP_200_OK
        )
