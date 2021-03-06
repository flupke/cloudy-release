"""
Django settings for cloudy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os.path as op

import environ

# Load environment
env = environ.Env(
    DEBUG=(bool, False),
    STATIC_ROOT=(str, None),
    ALLOWED_HOSTS=(list, []),
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = op.abspath(op.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%lg!q15vb4=-t=m3ph8@5-=c#r-8r&$byf3g3^(5-w%xp(df!u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'crispy_forms',

    'cloudy.projects',
    'cloudy.users',
    'cloudy.api',
    'cloudy.logs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cloudy.urls'

WSGI_APPLICATION = 'cloudy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cloudy',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True
DATETIME_FORMAT = 'Y-m-d H:i:s'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [op.join(BASE_DIR, 'static')]
STATIC_ROOT = env('STATIC_ROOT')

# Template settings
TEMPLATE_DIRS = [op.join(BASE_DIR, 'templates')]

# django-crispy-forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Auth settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'projects_list'

# Proxy settings
SECURE_PROXY_SSL_HEADER = ('X-Forwarded-Proto', 'https')

# Hide nodes that have not been seen since this number of hours
HIDE_NODES_AFTER = 1

# Logs settings
RECENT_HISTORY_ITEMS = 20
