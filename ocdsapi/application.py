from gevent import monkey; monkey.patch_all()

from flask import Flask
from flask_restful import Api
from ocdsapi.storage import ReleaseStorage
from ocdsapi.utils import build_meta
from pkg_resources import iter_entry_points


APP = Flask('ocdsapi')
API = Api(APP)


def make_paste_application(global_config, **options):
    APP.config['DEBUG'] = options.get('debug', False)
    APP.db = ReleaseStorage(
        options.get('couchdb_url'),
        options.get('couchdb_dbname'),
    )
    APP.config['metainfo'] = build_meta(options)
    for plugin in iter_entry_points('ocdsapi.resources'):
        includeme = plugin.load()
        includeme(options)
    return APP
