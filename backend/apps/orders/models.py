from django.db import models

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="Polska")

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        CANCELED = 'CANCELED', 'Canceled'

    # Relations
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    desk = models.ForeignKey('desks.Desk', on_delete=models.PROTECT)

    catalog_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)