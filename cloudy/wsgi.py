"""
WSGI config for cloudy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudy.settings")

try:
    # Make psycopg2 green
    import gevent.monkey
    gevent.monkey.patch_all()
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
