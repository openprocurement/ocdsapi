from urllib.parse import urljoin
from flask import request
from flask import url_for, abort
from flask_restful_swagger_2 import Resource

from .application import APP


class BaseResource(Resource):

    options = {}
    
    def __init__(self, options={}):
        self.db = APP.db
        self._options = options

    def _get(self, args):
        # Override this
        return {}
    
    def prepare_response(self):
        request_args = self.options.parse_args()
        item = self._get(request_args)
        if item:
            return item
        return abort(404)


class BaseCollectionResource(BaseResource):
    resource = ""

    def _prepare(self):
        raise NotImplementedError

    def prepare_next_url(self, params):
        if params.get('descending'):
            return url_for(
                self.resource,
                page=params['offset'],
                descending=params['descending']
                )
        else:
            return url_for(
                self.resource,
                page=params['offset'],
            )

    def prepare_uri(self):
        return request.url

    def prepare_response(self):
        request_args = self.options.parse_args()
        next_params = {}
        prev_params = {}
        descending = bool(request_args.descending)
        page = request_args.page
        if descending:
            next_params['descending'] = True
        else:
            prev_params['descending'] = True

        if page:
            view_offset = page
        else:
            view_offset = '9' if descending else ''
        last_key, results = self.db.page(
            view_offset,
            descending=descending,
            include_docs=True,
            view_limit=APP.paginate_by
        )

        if results:
            next_params['offset'] = last_key['date']
            prev_params['offset'] = results[0]['date']

            if page and view_offset == results[0]['date']:
                results = results[1:]
            elif page and view_offset != results[0]['date']:
                results = results[:100]
                next_params['offset'], prev_params['offset'] = last_key['date'], view_offset
        else:
            next_params['offset'] = page
            prev_params['offset'] = page
        response = self._prepare(request_args, results)
        response['links'] = {
            'next': urljoin(
                request.url_root,
                self.prepare_next_url(next_params)
            )
        }
        if page or descending:
            response['links']['prev'] = urljoin(
                request.url_root,
                self.prepare_next_url(prev_params)
            )
        return response
