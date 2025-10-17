## Chapa Payment Integration

### Environment
Set these env vars:
- CHAPA_SECRET_KEY
- CHAPA_BASE_URL (default: https://api.chapa.co)
- EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- Other Django env vars (SECRET_KEY, DB settings...)

### Start services
1. Run migrations:
    python manage.py makemigrations
    python manage.py migrate

2. Start Django server:
    python manage.py runserver

3. (Optional) Start Celery:
    celery -A alx_backend_graphql_crm worker -l info

### Initiate payment (sample curl)
curl -X POST http://localhost:8000/listings/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "amount": 100.50,
    "currency": "ETB",
    "customer_name": "Alice",
    "customer_email": "alice@example.com",
    "customer_phone": "+2519..."
}'

Response:
{
  "checkout_url": "https://checkout.chapa.co/....",
  "transaction_id": "...",
  "payment_id": 1
}

Open the checkout_url in your browser (or redirect user there) to complete payment (sandbox mode recommended).

### Verify payment (sample curl)
curl -X POST http://localhost:8000/listings/payments/verify/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"<id-returned-by-chapa>"}'

Response:
{
  "transaction": { ... },   # Chapa API response
  "status": "completed",
  "local_payment_id": 1
}

### Logs / Screenshots
1. Save JSON responses from `initiate` and `verify` to demonstrate success.
2. Include DB rows (e.g., `select * from listings_payment;`) or Django admin screenshots showing payment status updated.

