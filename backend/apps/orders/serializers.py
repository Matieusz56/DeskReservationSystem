from rest_framework import serializers
from decimal import Decimal
from decimal import ROUND_HALF_UP

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
    brand = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    catalogPricePLN = serializers.DecimalField(max_digits=10, decimal_places=2)

# Discount Code Schema
class DiscountSerializer(serializers.Serializer):
    isCodeApplied = serializers.BooleanField(default=False)
    discountCode = serializers.CharField(max_length=50,allow_null=True,required=False)
    discountPercentage = serializers.IntegerField(default=0,min_value=0,max_value=100)
    discountAmountPLN = serializers.DecimalField(max_digits=10,decimal_places=2, default=0.00)

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
        catalog_price = attrs['product']['catalogPricePLN']
        final_amount = attrs['summary']['finalAmountPLN']

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


class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_id = serializers.CharField()
    catalog_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_code = serializers.CharField(allow_null=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
