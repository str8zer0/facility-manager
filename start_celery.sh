#!/bin/bash
set -e

echo "Starting Celery worker..."
exec celery -A facility_manager worker --loglevel=info
