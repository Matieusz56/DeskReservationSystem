from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Address, Customer, Order


VALID_PAYLOAD = {
    'customer': {
        'firstName': 'Jan',
        'lastName': 'Kowalski',
        'phoneNumber': '+48600111222',
        'email': 'jan.kowalski@example.com',
        'address': {
            'street': 'Marszalkowska 10/12',
            'city': 'Warszawa',
            'postalCode': '00-001',
            'country': 'Polska',
        },
    },
    'product': {
        'id': 'desk_9821',
        'brand': 'IKEA',
        'model': 'BEKANT',
        'name': 'Biurko',
        'catalogPricePLN': '1299.00',
    },
    'discount': {
        'isCodeApplied': True,
        'discountCode': 'LATO2026',
        'discountPercentage': 10,
        'discountAmountPLN': '129.90',
    },
    'summary': {
        'finalAmountPLN': '1169.10',
        'currency': 'PLN',
    },
}


class OrderCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_creates_order_and_related_records(self):
        response = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(response.data['status'], Order.Status.PENDING)
        self.assertEqual(Decimal(response.data['final_price']), Decimal('1169.10'))

    def test_rejects_invalid_final_price_without_persistence(self):
        payload = {
            **VALID_PAYLOAD,
            'summary': {**VALID_PAYLOAD['summary'], 'finalAmountPLN': '100.00'},
        }

        response = self.client.post('/api/orders/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertEqual(Address.objects.count(), 0)

    def test_rejects_inconsistent_discount(self):
        payload = {
            **VALID_PAYLOAD,
            'discount': {
                **VALID_PAYLOAD['discount'],
                'discountAmountPLN': '100.00',
            },
        }

        response = self.client.post('/api/orders/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
