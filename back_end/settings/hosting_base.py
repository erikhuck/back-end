import os

from back_end.settings.base import *

DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
WSGI_APPLICATION = 'back_end.wsgi.application'
CORS_ORIGIN_ALLOW_ALL = False

MIDDLEWARE += [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware'
]

SECURE_HSTS_SECONDS = 3
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True
