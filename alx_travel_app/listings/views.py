from django.shortcuts import render

# Create your views here.
# listings/views.py
import os
import requests
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Payment, Booking
from .tasks import send_payment_confirmation_email  # celery task (see below)
from django.views.decorators.http import require_POST
import json
import uuid
from rest_framework import viewsets
from .serializers import BookingSerializer
from .tasks import send_booking_confirmation_email

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        user_email = booking.user.email if booking.user else None

        if user_email:
            # Trigger Celery background email task
            send_booking_confirmation_email.delay(user_email, booking.id)

from rest_framework import viewsets
from .serializers import BookingSerializer
from .tasks import send_booking_confirmation_email

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        user_email = booking.user.email if booking.user else None

        if user_email:
            # Trigger Celery background email task
            send_booking_confirmation_email.delay(user_email, booking.id)

CHAPA_BASE = getattr(settings, 'CHAPA_BASE_URL', 'https://api.chapa.co')
CHAPA_SECRET = getattr(settings, 'CHAPA_SECRET_KEY', None)

HEADERS = {
    "Authorization": f"Bearer {CHAPA_SECRET}",
    "Content-Type": "application/json"
}

@csrf_exempt
@require_POST
def initiate_payment(request):
    """
    Initiate a payment:
    Expected JSON body:
    {
      "booking_id": 1,
      "amount": 100.50,
      "currency": "ETB",
      "customer_name": "Alice",
      "customer_email": "simonbayu2211@gmail.com",
      "customer_phone": "+2519..."
    }
    Response: { "checkout_url": "...", "transaction_id": "..." }
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    booking_id = payload.get("booking_id")
    amount = payload.get("amount")
    currency = payload.get("currency", "ETB")
    name = payload.get("sewmehon")
    email = payload.get("simonbayu2211@gmail.com")
    phone = payload.get("customer_phone")

    if not (booking_id and amount and email):
        return JsonResponse({"error": "booking_id, amount and customer_email are required"}, status=400)

    # find booking (optional)
    booking = None
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        # fallback: proceed but leave booking null
        booking = None

    # create local payment record
    unique_transaction_id = str(uuid.uuid4())
    payment = Payment.objects.create(
        booking=booking,
        booking_reference=(booking.reference if booking else ""),
        amount=Decimal(str(amount)),
        currency=currency,
        transaction_id=unique_transaction_id,
        status='pending'
    )

    # Prepare payload for Chapa initiate
    # Note: Chapa's "initialize" endpoint expects amount, currency, description, firstname/lastname/email, callback_url, and return_url typically.
    # Use Chapa's docs for exact keys — this is a typical pattern.
    chapa_payload = {
        "amount": str(amount),
        "currency": currency,
        "tx_ref": unique_transaction_id,   # client transaction ref
        "customer_name": name or "",
        "customer_email": email,
        "customer_phone": phone or "",
        # callback and return url: adjust your domain
        "callback_url": payload.get("callback_url") or "http://localhost:8000/payments/verify/",
        "return_url": payload.get("return_url") or "http://localhost:8000/payment/success/",
        "customization": {
            "title": "Booking payment",
            "description": f"Payment for booking {booking.reference if booking else ''}"
        }
    }

    # call Chapa initialize endpoint - endpoint path may differ, check docs
    try:
        resp = requests.post(
            f"{CHAPA_BASE}/v1/transaction/initialize",  # common path, verify with docs
            headers=HEADERS,
            json=chapa_payload,
            timeout=15
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        payment.status = 'failed'
        payment.metadata = {'error': str(e)}
        payment.save()
        return JsonResponse({"error": "Failed to contact payment gateway", "details": str(e)}, status=502)

    data = resp.json()

    # Example response parsing - adapt to actual Chapa response format
    # Successful init often contains 'status':'success' and 'data' with checkout_url & id
    chapa_data = data.get('data') or data
    checkout_url = chapa_data.get('checkout_url') or chapa_data.get('url') or None
    chapa_tx_id = chapa_data.get('id') or chapa_data.get('transaction_id') or None

    # update payment with returned info
    payment.chapa_checkout_url = checkout_url
    # if Chapa returns an authoritative transaction id, store it (while preserving our tx_ref)
    if chapa_tx_id:
        payment.transaction_id = chapa_tx_id
    payment.metadata = chapa_data
    payment.save()

    return JsonResponse({
        "checkout_url": checkout_url,
        "transaction_id": payment.transaction_id,
        "payment_id": payment.id
    })



@csrf_exempt
@require_POST
def verify_payment(request):
    """
    Verify payment using transaction id or tx_ref.
    Expected JSON body:
    { "transaction_id": "<id>" }  OR { "tx_ref": "<your tx ref>" }
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    chapa_id = payload.get("transaction_id")
    tx_ref = payload.get("tx_ref") or payload.get("transaction_ref")

    if not (chapa_id or tx_ref):
        return JsonResponse({"error": "transaction_id or tx_ref required"}, status=400)

    # find Payment record
    payment = None
    if chapa_id:
        payment = Payment.objects.filter(transaction_id=chapa_id).first()
    else:
        # our stored tx_ref could be in transaction_id column if we used uuid before initialize
        payment = Payment.objects.filter(transaction_id=tx_ref).first()

    # fallback: if not found, continue verification but no local record
    # Call Chapa verify endpoint (path depends on Chapa's API)
    # Example: GET /v1/transaction/verify/:tx_ref or /v1/transaction/:id
    try:
        if tx_ref and not chapa_id:
            verify_url = f"{CHAPA_BASE}/v1/transaction/verify/{tx_ref}"
        else:
            # some APIs use id verify
            verify_url = f"{CHAPA_BASE}/v1/transaction/verify/{chapa_id}"
        resp = requests.get(verify_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to contact payment gateway", "details": str(e)}, status=502)

    data = resp.json()
    chapa_data = data.get('data') or data

    # Example: chapa_data may include status like 'success' or 'failed' and relevant fields
    status = chapa_data.get('status') or data.get('status') or 'unknown'
    # Normalize statuses - adapt mapping to Chapa's real response
    if status in ['success', 'completed', 'paid']:
        new_status = 'completed'
    elif status in ['failed', 'cancelled', 'declined']:
        new_status = 'failed'
    else:
        new_status = 'pending'

    if payment:
        payment.status = new_status
        payment.metadata = chapa_data
        payment.updated_at = timezone.now()
        payment.save()

        # on completed, kick off confirmation email via Celery
        if new_status == 'completed' and payment.booking:
            send_payment_confirmation_email.delay(payment.id)

    return JsonResponse({
        "transaction": chapa_data,
        "status": new_status,
        "local_payment_id": payment.id if payment else None
    })
