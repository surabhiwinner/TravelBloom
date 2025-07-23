web: python travelbloom/manage.py collectstatic --noinput && gunicorn travelbloom.wsgi:application --chdir travelbloom --bind 0.0.0.0:$PORT --log-file -
