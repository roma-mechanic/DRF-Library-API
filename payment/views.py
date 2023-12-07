import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from DRF_Library_API import settings
from borrowing.models import Borrowing
from bot.main_bot import telegram_bot_sendtext
from payment.models import Payment
from payment.serializers import PaymentSerializer


def create_item_attr_dict(book):
    item_attr_dict = {
        "price_data": {
            "currency": "usd",
            "unit_amount": int(book.daily_fee * settings.BORROWING_DAYS * 100),
            "product_data": {
                "name": book.title,
            },
        },
        "quantity": 1,
    }
    return item_attr_dict


@csrf_exempt
def create_checkout_session(borrow_id, request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    borrow = Borrowing.objects.get(id=borrow_id)
    books = borrow.book.all().prefetch_related("book")

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse("payment:success"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("payment:failed")),
            payment_method_types=["card"],
            mode="payment",
            line_items=[create_item_attr_dict(book) for book in books],
        )
    except Exception as err:
        return JsonResponse({"error": str(err)})
    else:
        payment = Payment()
        payment.borrowing = borrow
        payment.session_id = checkout_session.id
        payment.session_url = checkout_session.url
        payment.money_to_pay = borrow.total_cost
        payment.save()
    return redirect(checkout_session.url, code=303)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def get_queryset(self):
        qs = super().get_queryset()
        current_user = self.request.user
        if not current_user.is_staff and not current_user.is_superuser:
            qs = qs.filter(customer_email=self.request.user.email)

        return qs


def payment_success_view(request):
    session_id = request.GET["session_id"]
    payment = get_object_or_404(Payment, session_id=session_id)
    user = payment.borrowing.user

    if payment.status == "pending":
        payment.status = "paid"
        payment.save()

    message = (
        f"{payment.borrowing.user.username}.\n "
        f"Your order {payment.borrowing.pk} is paid and created {payment.borrowing.borrow_date}\n"
        f"Date of return of books {payment.borrowing.expected_return_date}\n"
        f"Your payment status is {payment.status}\n"
        f"If the deadline is overdue,"
        f" you will need to pay an additional fine for overdue days"
        f" in the amount of double the cost of the order"
    )
    telegram_bot_sendtext(message, user.telebot_chat_ID)

    return redirect(reverse("borrowing:borrowing-list"))


def payment_failed_view(request):
    return "Payment can be paid a bit later (but the session is available for only 24h)"
