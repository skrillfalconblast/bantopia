release: python manage.py migrate
web: daphne Lyceum.asgi:application --port 8000 --bind 0.0.0.0 -v2
channel_worker: python manage.py runworker channel_layer -v2
