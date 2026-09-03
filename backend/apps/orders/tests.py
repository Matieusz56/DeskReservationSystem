from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from apps.desks.models import Desk
from .models import Address, Customer, Order

VALID_PAYLOAD = {
  "customer": {
    "firstName": "Jan",
    "lastName": "Kowalski",
    "phoneNumber": "+48600111222",
    "email": "jan.kowalski@example.com",
    "address": {
      "street": "Marszałkowska 10/12",
      "city": "Warszawa",
      "postalCode": "00-001",
      "country": "Polska"
    }
  },
  "product": {
    "id": "desk_9821"
  },
  "discount": {
    "isCodeApplied": True,
    "discountCode": "LATO2026",
    "discountPercentage": 10,
    "discountAmountPLN": 129.90
  },
  "summary": {
    "finalAmountPLN": 1169.10,
    "currency": "PLN"
  }
}


class OrderCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.desk = Desk.objects.create(
            external_id='desk_9821',
            brand='IKEA',
            model='BEKANT',
            name='Biurko z regulacją wysokości 160x80',
            catalog_price=Decimal('1299.00'),
            stock_quantity=10,
        )

    def test_creates_order_and_related_records(self):
        response = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(Order.objects.get().desk, self.desk)
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

    def test_get_existing_order(self):
        create_response = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')
        self.assertEqual(create_response.status_code, 201)

        order_id = create_response.data['id']
        response = self.client.get(f'/api/orders/{order_id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], order_id)
        self.assertEqual(response.data['desk']['external_id'], 'desk_9821')
        self.assertEqual(response.data['desk']['brand'], 'IKEA')
        self.assertEqual(response.data['desk']['model'], 'BEKANT')
        self.assertEqual(response.data['catalog_price'], '1299.00')
        self.assertEqual(response.data['desk']['stock_quantity'], 10)

    def test_get_non_existing_order(self):
        response = self.client.get('/api/orders/9999/')

        self.assertEqual(response.status_code, 404)

    def test_get_every_order(self):
        create_response1 = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')
        create_response2 = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')
        create_response3 = self.client.post('/api/orders/', VALID_PAYLOAD, format='json')
        self.assertEqual(create_response1.status_code, 201)
        self.assertEqual(create_response2.status_code, 201)
        self.assertEqual(create_response3.status_code, 201)

        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data),3)