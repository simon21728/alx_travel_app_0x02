"""
Django settings for alx_travel_app project.
"""

from pathlib import Path
import environ
import os

# ---------------- Environment setup ----------------
env = environ.Env()
environ.Env.read_env()  # load variables from .env file

# ---------------- Base directory ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- Security ----------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="your-default-secret-key")
DEBUG = True
ALLOWED_HOSTS = []

# ---------------- Installed apps ----------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'listings',                  # your app
    'django_celery_results',     # if using Celery result backend
]

# ---------------- Middleware ----------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------- URLs and WSGI ----------------
ROOT_URLCONF = 'alx_travel_app.urls'
WSGI_APPLICATION = 'alx_travel_app.wsgi.application'


# ---------------- Templates ----------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional, for project-level templates
        'APP_DIRS': True,                  # important: allows Django to find app templates (including admin)
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required by admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ---------------- Database ----------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------- Password validation ----------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------- Internationalization ----------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------- Static files ----------------
STATIC_URL = 'static/'

# ---------------- Default primary key ----------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------- Email configuration ----------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="your-email@gmail.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="your-email-password")
EMAIL_USE_TLS = True

# ---------------- Chapa configuration ----------------
CHAPA_SECRET_KEY = env("CHAPA_SECRET_KEY", default="CHASECK_TEST-862lbo3BT7FwdgLVuBdfzfgEE6MfNcEO")
CHAPA_BASE_URL = env("CHAPA_BASE_URL", default="https://api.chapa.co")

# ---------------- Celery configuration ----------------
CELERY_RESULT_BACKEND = "django-db"
