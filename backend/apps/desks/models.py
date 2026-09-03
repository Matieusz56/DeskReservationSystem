from django.core.validators import MinValueValidator
from django.db import models

class Desk(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    catalog_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.external_id})"