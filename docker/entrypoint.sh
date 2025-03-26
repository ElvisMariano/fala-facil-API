#!/bin/sh

set -e

# Função para esperar serviços
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "Waiting for $service..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service started"
}

# Espera serviços iniciarem
wait_for_service db 5432 "PostgreSQL"
wait_for_service redis 6379 "Redis"

# Aplica as migrações
echo "Applying database migrations..."
poetry run python src/manage.py migrate --noinput

# Coleta arquivos estáticos em produção
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    echo "Collecting static files..."
    poetry run python src/manage.py collectstatic --noinput
fi

# Inicia o servidor
echo "Starting server..."
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 4
else
    poetry run python src/manage.py runserver 0.0.0.0:8000 