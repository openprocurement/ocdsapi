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
from .utils import prepare_responce_doc, ids_only, find_max_date


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("releaseID", type=str)
collection_options.add_argument("descending", type=bool)

item_options = reqparse.RequestParser()
item_options.add_argument(
    "releaseID",
    type=str,
    required=True,
    )


class ReleaseResource(BaseResource):

    options = item_options

    def _get(self, request_args):
        if not request_args.releaseID:
            return {}
        return self.db.get_id(request_args.releaseID)

    @swagger.doc({
        "summary" : "Returns an OCDS release",
        "description" : "This should return an OCDS release object. There is potential for releaseIds to be duplicated for a particular API.  If this is the case then the user should provide either a packageURL or an ocid in order to get an individual release.",
        "responses": {
            "200": {"description": "Single Release"}
        },
        "parameters": [
          {
            "in": "query",
            "name": "releaseID",
            "required": True,
            "type": "string",
            "description": "The release id of the release"
          }
        ]
    })
    def get(self):
        return self.prepare_response()


class ReleasesResource(BaseCollectionResource):

    resource = 'releases.json'
    options = collection_options

    def _prepare(self, args, response_data):
        if args.idsOnly:
            releases = [
                ids_only(item['doc'])
                for item in response_data
            ]
        else:
            releases = [
                item['doc']
                for item in response_data
            ]
        return {
            'releases': releases,
            'uri': self.prepare_uri(),
            'publishedDate': find_max_date(response_data),
            **app.config['metainfo']
        }
    
    @swagger.doc({
        "summary" : "Returns OCDS records",
        "description" : "This should return an object and in it should be a OCDS records list and links object.  The links object should have a 'next' property with the url of the next url that is to visited when paging through the results.  Normally a full OCDS record should be in the 'records' list.  The results should be listed in modified date descending.",
        "responses": {
            "200": {"description": "List of records"}
        },
        "parameters": [
          {
            "in": "query",
            "name": "idsOnly",
            "type": "string",
            "description": "A list of objects is returned but contiains only the 'ocid' and 'id' properties. Useful for large datasets where you just want to see what new records ther are."
          },{
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
        ReleasesResource, 
        '/api/releases.json',
        endpoint='releases.json',
        resource_class_kwargs={"options": options}
    )
    API.add_resource(
        ReleaseResource,
        '/api/release.json',
        endpoint='release.json',
        resource_class_kwargs={"options": options}
    )
    
