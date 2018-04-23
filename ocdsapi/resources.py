import arrow
from urllib.parse import urljoin
from datetime import timedelta
from flask import current_app as app
from flask import url_for, request
from flask_restful import Resource, reqparse, marshal, abort
from iso8601 import parse_date
from repoze.lru import lru_cache
from .marshal import releases
from .paginate import PaginationHelper




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
        self.skip_empty = kw.get('skip_empty')
        self.kw = kw
    
    def filter_release_id(self, data, release_id):
        if release_id:
            return [
                item for item in data
                if item == release_id
            ]
        return data

    def prepare_prev_url(self, start_date, end_date):
        if self.skip_empty:
            result = ''
            while True:
                end_date = start_date
                start_date = PaginationHelper.format(arrow.get(end_date) - timedelta(days=1))
                if start_date < self.db.min_date():
                    return ""
                result = self.db.ids_inside(start_date, end_date)
                if result:
                    break
        return self.pager.prev_url(start_date)

    def prepare_next_url(self, start_date, end_date):
        if self.skip_empty:
            result = ''
            while True:
                start_date = end_date
                end_date = PaginationHelper.format(arrow.get(start_date) + timedelta(days=1))
                if end_date > self.db.max_date():
                    ""
                result = self.db.ids_inside(start_date, end_date)
                if result:
                    break
        return self.pager.next_url(start_date)

    @lru_cache(maxsize=1000)
    def _prepare_links(self, page):
        links = {}
        if page:
            start_date, end_date = self.pager.decode_page(
                page
                )
            prev = self.prepare_prev_url(start_date, end_date) 
            if prev:
                links['prev'] = prev
        else:
            start_date, end_date = self.pager.prepare_initial_offset()
        next = self.prepare_next_url(start_date, end_date)
        if next:
            links['next'] = next
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
        result = {
            'publishedDate': end_date,
            'links': links,
            'uri': request.full_path,
            **app.config['metainfo']
        }
        fields = releases(result)
            
        if request_args.idsOnly:
            result['releases'] = self.filter_release_id(
                self.db.ids_inside(start_date, end_date),
                request_args.releaseID
            )
        else:
            result['releases'] = [
                    urljoin(
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
