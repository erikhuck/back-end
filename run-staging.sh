source .env/bin/activate

DJANGO_SETTINGS_MODULE=back_end.settings.staging gunicorn back_end.wsgi -b 0.0.0.0:8000