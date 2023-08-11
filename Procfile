release: python manage.py migrate
web: daphne Lyceum.asgi:application
worker: python manage.py runworker channels --settings=Lyceum.settings -v2