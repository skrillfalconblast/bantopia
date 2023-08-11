release: python Lyceum/manage.py migrate
web: daphne Lyceum.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python Lyceum/manage.py runworker channels --settings=Lyceum.settings -v2