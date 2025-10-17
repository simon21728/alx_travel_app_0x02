from django.db import models

# Create your models here.
# listings/models.py
from django.conf import settings

class Booking(models.Model):
    # Minimal example booking model; replace with your real one
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # other booking fields...

    def __str__(self):
        return f"Booking {self.reference}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    booking_reference = models.CharField(max_length=64, blank=True)  # in case you want to store ref without relation
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='ETB')
    transaction_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    chapa_checkout_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(null=True, blank=True)  # store Chapa response raw data

    def __str__(self):
        return f"Payment {self.id} ({self.status}) for {self.booking_reference or self.booking_id}"
