from urllib.parse import urljoin
from flask import request
from flask import url_for


class BaseCollectionResource:
    resource = ""
    options = {}

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
        last_key, results = self.db.page(view_offset, descending=descending)
        gettter = lambda item: item[1]
        if results:
            next_params['offset'], prev_params['offset'] = last_key, gettter(results[0])
            if page and view_offset == gettter(results[0]):
                results = results[1:]
            elif page and view_offset != results[0][1]:
                results = results[:100]
                next_params['offset'], prev_params['offset'] = last_key, view_offset
        else:
            next_params['offset'] = page
            prev_params['offset'] = page
        data = {
            'next': next_params,
            'prev': prev_params,
            'data': results
        }
        resp = self._prepare(request_args, data)
        resp['links'] = {
            'next': urljoin(
                request.url_root,
                self.prepare_next_url(data['next'])
            )
        }
        if page or descending:
            resp['links']['prev'] = urljoin(
                request.url_root,
                self.prepare_next_url(data['prev'])
            )
        return resp