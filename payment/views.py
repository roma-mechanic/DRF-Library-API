import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import RedirectView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from DRF_Library_API import settings
from borrowing.models import Borrowing
from payment.models import Payment


def create_item_attr_dict(item, count=1):
    item_attr_dict = {
        "price_data": {
            "currency": "usd",
            "unit_amount": int(item.price * 100),
            "product_data": {
                "name": item.name,
            },
        },
        "quantity": count,
    }
    return item_attr_dict


def create_line_items_single_purchase(item):
    return [create_item_attr_dict(item)]


def create_checkout_session(line_creation_func, item_object):
    domain_url = settings.DOMAIN_URL
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=(
                domain_url + "success?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=domain_url + "cancel/",
            payment_method_types=["card"],
            mode="payment",
            line_items=line_creation_func(item_object),
        )
    except Exception as err:
        return JsonResponse({"error": str(err)})
    else:
        return checkout_session


class PurchaseView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        item = Borrowing.objects.get(pk=self.kwargs.get("pk"))
        session = create_checkout_session(
            create_line_items_single_purchase, item
        )
        return redirect(session.url, code=303)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)
