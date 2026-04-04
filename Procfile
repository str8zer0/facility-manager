web: celery -A facility_manager worker --loglevel=info & python manage.py migrate --noinput && gunicorn facility_manager.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
