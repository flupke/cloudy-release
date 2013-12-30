Cloudy Release (with a chance of sunshine)
==========================================

.. image:: https://requires.io/github/flupke/cloudy-release/requirements.png?branch=develop
   :target: https://requires.io/github/flupke/cloudy-release/requirements/?branch=develop
   :alt: Requirements Status

Cloudy Release is a system for deploying applications.

It tries to solve these common problems:

* how do I keep nodes that were offline during the last deployment up-to-date?

* how can I make sure the deployment went well?

* how do I deploy my app on multiple nodes with different configurations?

Cloudy Release tries to answer these problems simply:

* `clients <https://github.com/flupke/cloudy-release-client>`_ are installed on
  the hosts where the applications are deployed. They regularly poll the server
  and deploy updates when necessary. If a host goes down when an update is
  triggered, it will catch up on its next reboot;

* the web interface gives an overview to check deployment details;

* projects can have different deployment configurations, with different
  variables (for example a website could have production and testing
  deployments, with different database settings). The variables then are
  transmitted to the clients, which pass them to deployment scripts.

Compared to Fabric, deployments are faster because deployment scripts are run
locally by the clients, you have a place to check if something went wrong
with your deployments, and you can write template deployment scripts driven by
configuration (you can do this to some extent with Fabric using roles, but
roles are tied to hosts, you can't deploy production + testing variants of your
site on the same host without ugly hacks).


Installation example
====================

Here is an example for serving the Cloudy Release server with nginx,
postgresql, uwsgi+gevent and supervisor.

Install system dependencies ()::

    sudo apt-get install build-essential libpq-dev python-dev nginx \
        postgresql supervisor python-pip python-virtualenv

Create a PostgreSQL database for the site::

    sudo su postgres
    createdb -E utf8 -O cloudy cloudy
    exit

Create an user for the running the site::

    adduser cloudy
    sudo su cloudy
    cd /home/cloudy

Create a virtualenv::

    virtualenv venv
    source venv/bin/activate

Create a directory for holding static files::

    mkdir static

Clone the repository and checkout the develop branch::

    git clone https://github.com/flupke/cloudy-release.git
    cd cloudy-release
    git checkout develop

Install requirements (in this example we are going to serve the site with
uWSGI and gevent)::

    pip install -r requirements.txt
    pip install gevent uwsgi psycogreen

Initialize database::

    ./manage.py syncdb
    ./manage.py migrate

Put local settings in ``cloudy/settings/local.py``::

    DEBUG = False
    TEMPLATE_DEBUG = False
    STATIC_ROOT = '/home/cloudy/static'
    ALLOWED_HOSTS = ['cloudy.example.com']

Create a nginx configuration in
``/etc/nginx/sites-enables/cloudy.example.com``::

    server {
        listen 80;
        server_name cloudy.example.com;

        location /static {
            alias /home/cloudy/static;
        }

        location / {
            uwsgi_pass unix:///tmp/cloudy.sock;
            include uwsgi_params;
        }
    }

Create a `supervisord <http://supervisord.org/>`_ configuration file in
``/etc/supervisor/conf.d/cloudy.conf``::

    [program:cloudy]
    command=/home/cloudy/venv/bin/uwsgi
        --module cloudy.wsgi:application
        --env DJANGO_SETTINGS_MODULE=cloudy.settings
        --master
        --pidfile=/tmp/cloudy.pid
        --socket /tmp/cloudy.sock
        --chmod-socket=666
        --disable-logging
        --processes 2
        --gevent 64
    user = cloudy
    group = cloudy
    autostart = true
    autorestart = true
    redirect_stderr = true
    directory = /home/cloudy/cloudy-release
    stopsignal = QUIT
    stopwaitsecs = 10

And finally start the site's process::

    sudo supervisorctl update

If all went well the site should be available on http://cloudy.example.com\.
