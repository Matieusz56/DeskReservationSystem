from django.db import transaction

from .models import Address, Customer, Order
from apps.desks.models import Desk


@transaction.atomic
def create_order(validated_data):
    customer_data = validated_data['customer']
    address_data = customer_data['address']
    product_data = validated_data['product']
    discount_data = validated_data.get('discount', {})
    summary_data = validated_data['summary']

    desk = Desk.objects.get(
        external_id=product_data['id'],
    )

    address = Address.objects.create(
        street=address_data['street'],
        city=address_data['city'],
        postal_code=address_data['postalCode'],
        country=address_data.get('country', 'Polska'),
    )
    customer = Customer.objects.create(
        first_name=customer_data['firstName'],
        last_name=customer_data['lastName'],
        phone_number=customer_data['phoneNumber'],
        email=customer_data['email'],
        address=address,
    )
    return Order.objects.create(
        customer=customer,
        desk=desk,
        catalog_price=desk.catalog_price,
        discount_code=discount_data.get('discountCode'),
        final_price=summary_data['finalAmountPLN'],
    )
