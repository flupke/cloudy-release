"""
WSGI config for cloudy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudy.settings")

import gevent_psycopg2
gevent_psycopg2.monkey_patch()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
