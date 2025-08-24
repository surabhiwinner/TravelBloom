release: python manage.py collectstatic --noinput
web: gunicorn travelbloom.travelbloom.wsgi:application --bind 0.0.0.0:$PORT --log-file -
