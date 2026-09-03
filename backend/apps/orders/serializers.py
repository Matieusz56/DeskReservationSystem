from rest_framework import serializers
from decimal import Decimal
from decimal import ROUND_HALF_UP

from apps.desks.models import Desk

# Address Schema
class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=200)
    postalCode = serializers.CharField(max_length=10)
    country = serializers.CharField(max_length=100)

# Customer Schema
class CustomerSerializer(serializers.Serializer):
    firstName = serializers.CharField(max_length=100)
    lastName = serializers.CharField(max_length=100)
    phoneNumber = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    address = AddressSerializer()

# Product Schema
class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50)

# Discount Code Schema
class DiscountSerializer(serializers.Serializer):
    isCodeApplied = serializers.BooleanField(default=False)
    discountCode = serializers.CharField(max_length=50,allow_null=True,required=False)
    discountPercentage = serializers.IntegerField(default=0,min_value=0,max_value=100)
    discountAmountPLN = serializers.DecimalField(max_digits=10,decimal_places=2, default=Decimal('0.00'))

# Summary Schema
class SummarySerializer(serializers.Serializer):
    finalAmountPLN = serializers.DecimalField(max_digits=10,decimal_places=2)
    currency = serializers.CharField(max_length=3, default='PLN')

# -------------------------------------------
# MAIN ORDER SERIALIZER
# -------------------------------------------
class DeskOrderSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    product = ProductSerializer()
    discount = DiscountSerializer(required=False)
    summary = SummarySerializer()

    def validate(self, attrs):
        product_id = attrs['product']['id']
        final_amount = attrs['summary']['finalAmountPLN']

        try:
            desk = Desk.objects.get(external_id=product_id)
        except Desk.DoesNotExist:
            raise serializers.ValidationError({
                'product': f"Desk '{product_id}' does not exist.",
            })

        if desk.stock_quantity < 1:
            raise serializers.ValidationError({
                'product': f"Desk '{product_id}' is out of stock.",
            })

        catalog_price = desk.catalog_price
        discount_data = attrs.get('discount', {})
        discount_amount = discount_data.get('discountAmountPLN', Decimal('0.00'))
        discount_percentage = discount_data.get('discountPercentage', 0)
        is_code_applied = discount_data.get('isCodeApplied', False)
        expected_discount = (
            catalog_price * Decimal(discount_percentage) / Decimal('100')
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        errors = {}
        if discount_amount != expected_discount:
            errors['discount'] = (
                f"Invalid discount amount. Expected {expected_discount} PLN, "
                f"got {discount_amount} PLN."
            )
        if not is_code_applied and (discount_amount != Decimal('0.00') or discount_percentage != 0):
            errors['discount'] = 'Discount values require isCodeApplied=true.'
        if discount_amount > catalog_price:
            errors['discount'] = 'Discount cannot exceed the catalog price.'

        expected_amount = catalog_price - discount_amount

        if final_amount != expected_amount:
            errors['summary'] = (
                f"Invalid final amount. Expected {expected_amount} PLN, "
                f"got {final_amount} PLN."
            )
        if attrs['summary'].get('currency', 'PLN') != 'PLN':
            errors['summary'] = 'Only PLN currency is supported.'
        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class DeskResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    external_id = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    name = serializers.CharField()
    catalog_price = serializers.DecimalField(max_digits=10, decimal_places=2)   # actual price from catalog
    stock_quantity = serializers.IntegerField()

class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    desk = DeskResponseSerializer()
    catalog_price = serializers.DecimalField(max_digits=10, decimal_places=2)   # price saved in moment of buy
    discount_code = serializers.CharField(allow_null=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
