from django.contrib import admin

# Register your models here.
from .models import Payment
from .models import Booking
admin.site.register(Payment)
admin.site.register(Booking)