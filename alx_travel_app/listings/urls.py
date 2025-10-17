# listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('payments/initiate/', views.initiate_payment, name='payments-initiate'),
    path('payments/verify/', views.verify_payment, name='payments-verify'),
]
