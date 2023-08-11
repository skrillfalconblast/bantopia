release: python Lyceum/manage.py migrate
web: daphne Lyceum.asgi:application
worker: python Lyceum/manage.py runworker channels --settings=Lyceum.settings -v2