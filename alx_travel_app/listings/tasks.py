# listings/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
from django.utils import timezone

@shared_task
def send_booking_confirmation_email(user_email, booking_id):
    """
    Sends booking confirmation email asynchronously
    """
    subject = "Booking Confirmation"
    message = f"Your booking #{booking_id} has been successfully confirmed on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}."
    from_email = "noreply@alxtravelapp.com"
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    return f"Sent booking confirmation email to {user_email}"

@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.select_related('booking', 'booking__user').get(pk=payment_id)
    except Payment.DoesNotExist:
        return False

    # customize as needed
    subject = f"Payment confirmation for booking {payment.booking_reference or payment.booking_id}"
    message = f"""
    Hello,

    We have received your payment.
    Payment ID: {payment.transaction_id}
    Amount: {payment.amount} {payment.currency}
    Status: {payment.status}

    Thank you.
    """
    recipient = []
    if payment.booking and payment.booking.user and payment.booking.user.email:
        recipient = [payment.booking.user.email]
    else:
        # fallback or use stored email in metadata
        recipient_email = payment.metadata.get('customer_email') if payment.metadata else None
        if recipient_email:
            recipient = [recipient_email]

    if not recipient:
        return False

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
    return True
