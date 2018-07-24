from urllib.parse import urljoin
from flask import request
from flask import url_for
from flask import current_app as app
from flask_restful import reqparse
from flask_restful import marshal
from flask_restful import abort

from .core import BaseResource, BaseCollectionResource
from .utils import prepare_record, prepare_responce_doc, ids_only
from .application import API


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
            # TODO: multiple docs
            doc = self.db.get_ocid(request_args.ocid)
            if doc:
                record = prepare_record(doc, request_args.ocid)
                return record
        return abort(404)


class RecordsResource(BaseCollectionResource):

    resource = 'records.json'
    options = collection_options

    def _prepare(self, args, response_data):
        if args.idsOnly:
            records = [
                ids_only(item[-1])
                for item in response_data['data']
            ]
        else:
            records = [
                prepare_record(item[-1], item[-1].get('ocid'))
                for item in response_data['data']
            ]

        return {
            'uri': self.prepare_uri(),
            'publishedDate': response_data['next']['offset'],
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
