from django.db import models
from history.models import Order


class DeliveryDetails(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Delivery for Order {self.order.id} - {self.name}"