#!/bin/bash

set -e

# Wait for PostgreSQL
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Wait for Redis
until redis-cli -h "$REDIS_HOST" ping; do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 1
done

>&2 echo "Redis is up - executing command"

# Apply database migrations
echo "Applying database migrations..."
python src/manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python src/manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec "$@" 