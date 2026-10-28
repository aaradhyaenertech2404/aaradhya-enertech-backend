"""
WSGI shim for Render or hosting environments that default to `gunicorn app:app` or `app:application`.
Delegates to Django's `core.wsgi.application`.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
app = application
