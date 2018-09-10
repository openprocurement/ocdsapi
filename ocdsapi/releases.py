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
from .utils import prepare_responce_doc,\
    ids_only, find_max_date, read_datafile


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

releases_doc = read_datafile('releases.json')
release_doc = read_datafile('release.json')


class ReleaseResource(BaseResource):

    options = item_options

    def _get(self, request_args):
        if not request_args.releaseID:
            return {}
        return self.db.get_id(request_args.releaseID)

    @swagger.doc(release_doc)
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
    
    @swagger.doc(releases_doc)
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
    
