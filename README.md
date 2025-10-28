# ALX Travel App 0x03

This project demonstrates asynchronous background task management in Django using **Celery** with **RabbitMQ** and email notifications.

## Features
- Celery + RabbitMQ for background task queueing.
- Booking confirmation emails sent asynchronously.
- Django REST Framework for API endpoints.

## Setup
```bash
pip install -r requirements.txt
sudo service rabbitmq-server start
celery -A alx_travel_app worker -l info
python manage.py runserver
