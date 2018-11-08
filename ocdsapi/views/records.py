from urllib.parse import urljoin
from flask import request
from flask import url_for
from flask import current_app as app
from flask_restful import reqparse
from flask_restful import marshal
from flask_restful import abort
from flask_restful_swagger_2 import swagger

from .core import BaseResource, BaseCollectionResource
from .application import API
from .utils import prepare_record, prepare_responce_doc,\
    ids_only, find_max_date, read_datafile


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("descending", type=bool)

item_options = reqparse.RequestParser()
item_options.add_argument("ocid",
    type=str,
    required=True,
    )

records_doc = read_datafile('records.json')
record_doc = read_datafile('record.json')


class RecordResource(BaseResource):

    options = item_options

    def _get(self, request_args):
        if not request_args.ocid:
            return {  }
        return prepare_record(
            self.db.get_ocid(request_args.ocid)
        )

    @swagger.doc(record_doc)
    def get(self):
        return self.prepare_response()


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

    @swagger.doc(records_doc)
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
