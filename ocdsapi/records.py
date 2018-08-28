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

    options = item_options

    def _get(self, request_args):
        if not request_args.ocid:
            return {  }
        return prepare_record(
            self.db.get_ocid(request_args.ocid)
        )

    @swagger.doc({
        "summary" : "Returns an OCDS record",
        "description" : "This should return an OCDS record object.",
        "responses": {
            "200": {"description": "Single Record"}
            },
        "parameters": [
          {
            "in": "query",
            "name": "ocid",
            "required": True,
            "type": "string",
            "description": "The ocid of the record"
          }
        ]
    })
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
    
    @swagger.doc({
        "summary" : "Returns OCDS records",
        "description" : "This should return an object and in it should be a OCDS records list and links object.  The links object should have a 'next' property with the url of the next url that is to visited when paging through the results.  Normally a full OCDS record should be in the 'records' list.  The results should be listed in modified date descending.",
        "responses": {
            "200": {
                "description": "List of records"
                }
            },
        "parameters": [
          {
            "in": "query",
            "name": "idsOnly",
            "type": "string",
            "description": "A list of objects is returned but contiains only the 'ocid' and 'id' properties. Useful for large datasets where you just want to see what new records ther are."
          },
          {
            "in": "query",
            "name": "page",
            "type": "string",
            "description": "Ask for a specific page or results if server has paging"
          }
        ]
    })
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
