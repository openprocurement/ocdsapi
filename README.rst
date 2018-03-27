Documentation
=============

OCDS API is project which build an API over the OCDS releases database.

Building
--------

Use following commands to build :

``python bootstrap.py``

``bin/buildout -N``

``bin/supervisord``

Usage
--------
::

    bin/databridge -c etc/bridge.yaml

Run databridge to write OCDS releases to CouchDB database named releases.

::

    bin/runserver -c etc/config.yaml

Run Flask application which builds API on database. Default address to access it is http://127.0.0.1:5000

::

    bin/py.test

You can check everything using unit tests and this command runs it.

Views
----------

You can get api specification here https://github.com/open-contracting/api-specification. It is in swagger format, so here https://editor.swagger.io/ you can prettify output and get information about views.