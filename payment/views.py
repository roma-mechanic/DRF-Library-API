import stripe
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from DRF_Library_API import settings
from borrowing.models import Borrowing
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
    domain_url = settings.DOMAIN_URL
    stripe.api_key = settings.STRIPE_SECRET_KEY
    borrow = Borrowing.objects.get(id=borrow_id)
    books = borrow.book.all()

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

    def get_object(self):
        session_id = self.request.GET.get("session_id")
        payment = get_object_or_404(Payment, session_id=session_id)
        return payment

    def payment_success_view(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET.get("session_id")
        if session_id is None:
            return HttpResponseNotFound()
        session = stripe.checkout.Session.retrieve(session_id)
        payment = get_object_or_404(Payment, session_id=session_id)

        if payment.status == "pending":
            payment.status = "paid"
            payment.save()

        return f"Thanks for your order, {session.customer}"


def payment_failed_view(request):
    return "Payment can be paid a bit later (but the session is available for only 24h)"
