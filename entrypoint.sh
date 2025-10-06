#!/bin/sh

echo "Waiting for db..."
until nc -z db 5432; do
  sleep 1
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:8000 app.wsgi:application
