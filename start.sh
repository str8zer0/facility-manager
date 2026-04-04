#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating default admin user..."
python manage.py create_default_admin

echo "Starting Gunicorn..."
exec gunicorn facility_manager.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120