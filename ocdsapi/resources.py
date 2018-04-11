from flask import request, url_for, current_app as app, abort
from flask_restful import Resource, reqparse, abort, marshal
from iso8601 import parse_date
from ocdsapi.marshal import releases


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("packageURL", type=str)
collection_options.add_argument("releaseID", type=str)

release_options = reqparse.RequestParser()
release_options.add_argument(
    "releaseID",
    type=str,
    required=True,
    help="Provide valid releaseID"
    )
# release_options.add_argument("packageURL", type=str)  # TODO:
# release_options.add_argument("ocid", type=str)


class ReleaseResource(Resource):
    def __init__(self, **kw):
        self.db = kw.get('db')

    def get(self):
        request_args = release_options.parse_args()
        doc = self.db.get_id(request_args.releaseID)
        if doc:
            return doc
        return abort(404)
        # TODO: 
        #if not any((request_args.releaseID, request_args.ocid)):
        #    return abort(404)
        #if request_args.releaseID:
        #    return self.db.get_id(request_args.releaseID)
        #else:
        #    return self.db.get_ocid(request_args.ocid)


class ReleasesResource(Resource):

    def __init__(self, **kw):
        self.db = kw.get('db')
        self.pager = kw.get('paginator')
    
    def filter_release_id(self, data, release_id):
        if release_id:
            return [
                item for item in data
                if item == release_id
            ]
        return data

    def _prepare_links(self, page):
        links = {}
        if page:
            start_date, end_date = self.pager.decode_page(
                page
                )
            prev = self.pager.prepare_prev(page)
            if prev:
                links['prev'] = prev
        else:
            start_date, end_date = self.pager.prepare_initial_offset()
        next_params = self.pager.prepare_next(end_date)
        links['next'] = next_params
        return (
            start_date,
            end_date,
            links
        )

    def get(self):
        request_args = collection_options.parse_args()
        start_date, end_date, links = self._prepare_links(
            request_args.page
            )
        result = {}
        result.update(app.config['metainfo'])
        result['publishedDate'] = end_date
        result['links'] = links
        fields = releases(result)
        if request_args.idsOnly:
            result['releases'] = self.filter_release_id(
                    self.db.ids_inside(start_date, end_date),
                    request_args.releaseID
                    )
        else:
            result['releases'] = [
                    "{}{}".format(
                        request.url_root.strip('/'),
                        url_for('release.json', releaseID=id)
                        )
                    for id in self.filter_release_id(
                        self.db.ids_inside(start_date, end_date),
                        request_args.releaseID
                        )
                ]
        
        return marshal(result, fields)


def include(api, **kw):
    api.add_resource(
        ReleasesResource, 
        '/releases.json',
        endpoint='releases.json',
        resource_class_kwargs=kw
    )
    api.add_resource(
        ReleaseResource,
        '/release.json',
        endpoint='release.json',
        resource_class_kwargs=kw
    )
