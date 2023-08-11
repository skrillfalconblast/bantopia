"""
Django settings for Lyceum project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import environ
import dj_database_url
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', default='03mi2%8#pqyczpchxark+4*p@f_v4h(z5sgfx0n6xjjxnu2_(#')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'PRODUCTION' not in os.environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

CSRF_TRUSTED_ORIGINS = ['https://*.bantopia.com', 'http://127.0.0.1']

CSRF_FAILURE_VIEW = 'posts.views.csrf_failure'

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'posts',
    'chat',
    'admin_honeypot',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'debug_toolbar',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'Lyceum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Lyceum.wsgi.application'

# For the sites framework
SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if not DEBUG:
    DATABASE_URL = os.environ.get('DATABASE_URL')

    DATABASES = {
        'default': dj_database_url.config(
            # Feel free to alter this value to suit your needs.
            default=DATABASE_URL,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'lyceum_db',
            'USER': 'postgres',
            'PASSWORD': 'root', # SECUIRTY WARNING: you ought to secure these for production!
            'HOST': 'localhost'
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication backends

AUTHENTICATION_BACKENDS = [
    'users.backends.UserBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Sentry
if not DEBUG:
    sentry_sdk.init(
    dsn="https://f5ec0a343b4ff9770ce69cb49846e34f@o4505640849047552.ingest.sentry.io/4505640851341312",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
    )

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Safe Internal IPs for Django Debug Toolbar

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

if not DEBUG:
    # Tell Django to copy statics to the `staticfiles` directory
    # in your application directory
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.user'

ASGI_APPLICATION = "Lyceum.asgi.application"

if not DEBUG:
    REDIS_URL = os.environ.get('REDIS_URL')

    CHANNEL_LAYERS = {
        "default" : {
            "BACKEND" : "channels_redis.core.RedisChannelLayer",
            "CONFIG" : {
                "hosts" : [REDIS_URL],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        "default" : {
            "BACKEND" : "channels_redis.core.RedisChannelLayer",
            "CONFIG" : {
                "hosts" : [("127.0.0.1", 6379)],
            },
        },
    }

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CONN_MAX_AGE = None