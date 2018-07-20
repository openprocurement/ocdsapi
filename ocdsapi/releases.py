from urllib.parse import urljoin
from flask import request
from flask import url_for
from flask import current_app as app
from flask_restful import reqparse
from flask_restful import marshal
from flask_restful import abort

from .core import BaseResource, BaseCollectionResource
from .application import API


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("releaseID", type=str)
collection_options.add_argument("descending", type=bool)

item_options = reqparse.RequestParser()
item_options.add_argument(
    "releaseID",
    type=str,
    )
item_options.add_argument("ocid", type=str)


class ReleaseResource(BaseResource):

    def get(self):
        request_args = item_options.parse_args()
        if not any((request_args.releaseID, request_args.ocid)):
            return abort(404)

        if request_args.releaseID:
            doc = self.db.get_id(request_args.releaseID)
        else:
            doc = self.db.get_ocid(request_args.ocid)
        if doc:
            return doc
        return abort(404)


class ReleasesResource(BaseCollectionResource):

    resource = 'releases.json'
    options = collection_options

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
                    url_for('release.json', releaseID=id[0])
                    )
                for id in response_data['data']
            ]
        return {
            'releases': releases,
            'uri': self.prepare_uri(),
            'publishedDate': response_data['next']['offset'],
            **app.config['metainfo']
        }

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
    
