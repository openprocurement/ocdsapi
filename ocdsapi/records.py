from urllib.parse import urljoin
from flask import request
from flask import url_for
from flask import current_app as app
from flask_restful import reqparse
from flask_restful import marshal
from flask_restful import abort

from .core import BaseResource, BaseCollectionResource
from .application import API
from .utils import prepare_record, prepare_responce_doc,\
    ids_only, find_max_date


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("descending", type=bool)

item_options = reqparse.RequestParser()
item_options.add_argument("ocid",
    type=str, 
    required=True,
    )


class RecordResource(BaseResource):

    def get(self):
        request_args = item_options.parse_args()

        if request_args.ocid:
            record = prepare_record(
                self.db.get_ocid(request_args.ocid)
            )
            if record:
                return record
        return abort(404)


class RecordsResource(BaseCollectionResource):

    resource = 'records.json'
    options = collection_options

    def _prepare(self, args, response_data):
        if args.idsOnly:
            records = [
                ids_only(item['doc'])
                for item in response_data
            ]
        else:
            records = [
                prepare_record([item['doc']])
                for item in response_data
            ]

        return {
            'uri': self.prepare_uri(),
            'publishedDate': find_max_date(response_data),
            'records': records,
            **app.config['metainfo']
        }

    def get(self):
        return self.prepare_response()


def include(options):
    API.add_resource(
        RecordsResource, 
        '/api/records.json',
        endpoint='records.json',
        resource_class_kwargs={"options": options}
    )
    API.add_resource(
        RecordResource,
        '/api/record.json',
        endpoint='record.json',
        resource_class_kwargs={"options": options}
    )
