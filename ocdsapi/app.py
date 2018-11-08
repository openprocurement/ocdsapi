from gevent import monkey; monkey.patch_all()

import yaml
from flask import Flask
from flask_cors import CORS
from flask_restful_swagger_2 import Api
from werkzeug.contrib.fixers import ProxyFix
from ocdsapi.storage import ReleaseStorage
from ocdsapi.utils import build_meta, configure_extensions
from pkg_resources import iter_entry_points


DESCRIPTION = """
This OCDS API is built based on Version 1.1  of OCDS that  provides a scheme for publishing releases and records about contracting processes. The OCDS API helps to  make  contracting processes more transparent and accountable by providing a comprehensive, filterable OCDS data library. It supports publication of multiple releases and records in bulk ‘packages’, or as individual files, accessible at their own URIs and it returns data in an easily interpretable and scrapable JSON format.
"""
APP = Flask('ocdsapi')
CORS(APP)
APP.wsgi_app = ProxyFix(APP.wsgi_app) # Fixed proto on nginx proxy
API = Api(
    APP,
    api_version='0.1',
    api_spec_url='/api/swagger',
    description=DESCRIPTION,
    )


def make_paste_application(global_config, **options):
    APP.config['DEBUG'] = options.get('debug', False)
    APP.db = ReleaseStorage(
        options.get('couchdb_url'),
        options.get('couchdb_dbname'),
    )
    APP.paginate_by = options.get('paginate_by', 20)
    APP.config['metainfo'] = build_meta(options)
    swagger = options.get('swagger.file')
    if swagger:
        with open(swagger) as fd:
            swagger_info = yaml.load(fd)
        if swagger_info:
            API._swagger_object.update(swagger_info)
    APP.extensions = configure_extensions(options)
    for resource in iter_entry_points('ocdsapi.resources'):
        includeme = resource.load()
        includeme(options)
    return APP
