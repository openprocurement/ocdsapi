from urllib.parse import urljoin
from flask import request
from flask import url_for
from flask import current_app as app
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal
from flask_restful import abort

from .base import BaseCollectionResource
from .utils import prepare_record


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
# collection_options.add_argument("packageURL", type=str)
collection_options.add_argument("descending", type=bool)

item_options = reqparse.RequestParser()
# item_options.add_argument("packageURL", type=str)  # TODO:
item_options.add_argument("ocid",
    type=str, 
    required=True,
    )


class RecordResource(Resource):

    def __init__(self, **kw):
        self.db = kw.get('db')

    def get(self):
        request_args = item_options.parse_args()

        if request_args.ocid:
            doc = self.db.get_ocid(request_args.ocid)
            if doc:
                record = prepare_record(doc, request_args.ocid)
                return record
        return abort(404)


class RecordsResource(Resource, BaseCollectionResource):

    resource = 'records.json'
    options = collection_options

    def __init__(self, **kw):
        self.db = kw.get('db')
        self.skip_empty = kw.get('skip_empty')
        self.kw = kw

    def _prepare(self, args, response_data):
        if args.idsOnly:
            releases = [
                [item[0], item[2]]
                for item in response_data['data']
            ]
        else:
            releases = [
                urljoin(
                    request.url_root,
                    url_for('record.json', ocid=id[2])
                    )
                for id in response_data['data']
            ]

        return {
            'uri': request.full_path,
            'publishedDate': response_data['next']['offset'],
            'records': releases,
            **app.config['metainfo']
        }

    def get(self):
        return self.prepare_response()


def include(api, **kw):
    api.add_resource(
        RecordsResource, 
        '/api/records.json',
        endpoint='records.json',
        resource_class_kwargs=kw
    )
    api.add_resource(
        RecordResource,
        '/api/record.json',
        endpoint='record.json',
        resource_class_kwargs=kw
    )
