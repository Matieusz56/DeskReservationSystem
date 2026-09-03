from django.contrib import admin
from .models import Order, Customer, Address
# Register your models here.

admin.site.register(Address)
admin.site.register(Customer)
admin.site.register(Order)