from unittest import mock

import stripe
from rest_framework.test import APIClient, APITestCase, APIRequestFactory

from payment.models import Payment
from payment.views import (
    create_item_attr_dict,
    create_checkout_session,
    payment_success_view,
)
from test.sample_functions import (
    sample_user_profile_object,
    sample_book,
    sample_borrowing,
)


class CheckoutSessionResponseMock:
    id = "1"
    url = "http://127.0.0.1"
    amount_total = 1000


class PaymentTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user_profile_object()
        self.client.force_authenticate(user=self.user)

    def test_create_item_attr_dict(self):
        book = sample_book()
        item_dict = create_item_attr_dict(book, days=10)
        control_dict = {
            "price_data": {
                "currency": "usd",
                "unit_amount": 1000,
                "product_data": {"name": "Sample Book"},
            },
            "quantity": 1,
        }
        self.assertEqual(item_dict, control_dict)

    def test_create_checkout_session(self, **kwargs):
        with mock.patch.object(
            stripe.checkout.Session, "create"
        ) as mock_session:
            mock_session.return_value = CheckoutSessionResponseMock()
            print(mock_session.return_value.url)
            factory = APIRequestFactory()
            request = factory.get("payment")
            borrowing = sample_borrowing()
            test_session = create_checkout_session(
                borrowing.id,
                request,
                days=10,
                payment_status="pending",
                payment_type="payment",
            )
            print(test_session)
            mock_session.assert_called_once()

    @mock.patch("payment.views.telegram_bot_sendtext")
    def test_payment_success(self, mock_send_text, **kwargs):
        borrowing = sample_borrowing()
        payment = Payment.objects.get_or_create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=borrowing,
            session_id="3",
            session_url="https://example.com",
            money_to_pay=100.00,
        )

        factory = APIRequestFactory()
        request = factory.get(
            "http://127.0.0.1:8000/api/payment/success/?session_id=3"
        )
        payment_success_view(request)
        mock_send_text.assert_called_once()
