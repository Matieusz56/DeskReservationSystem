from rest_framework import serializers
from decimal import Decimal

# Address Schema
class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=200)
    postal_code = serializers.CharField(max_length=10)
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
    discounts = DiscountSerializer(required=False)
    summary = SummarySerializer()

    def validate(self, attrs):
        catalog_price = attrs['product']['catalogPricePLN']
        final_amount = attrs['summary']['finalAmountPLN']

        discount_data = attrs.get('discounts', {})
        discount_amount = discount_data.get('discountAmountPLN', Decimal('0.00'))

        expected_amount = catalog_price - discount_amount

        if final_amount != expected_amount:
            raise serializers.ValidationError({
                "summary": f"Invalid final amount. Expected {expected_amount} PLN, got {final_amount} PLN."
            })

        return attrs

