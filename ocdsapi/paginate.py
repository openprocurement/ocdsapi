from flask import current_app as app, url_for
from flask import request, abort

import base64
import arrow
from codecs import encode, decode
from datetime import timedelta


class PaginationHelper(object):
    
    def __init__(self, db):
        self.db = db

    def encode_page(self, start_date, end_date):
        data = '--'.join((start_date, end_date))
        return data

    def decode_page(self, page):
        return page.split('--')

    def _get_min(self):
        return arrow.get(self.db.min_date())

    def format(self, date):
        return date.format("YYYY-MM-DD")
    
    def prepare_initial_offset(self):
        start_date = self._get_min()
        return (
            self.format(start_date),
            self.format(start_date+timedelta(days=1))
            )

    def prepare_next(self, start_date):
        end_date = arrow.get(start_date) + timedelta(days=1)
        page = self.encode_page(
            self.format(start_date),
            self.format(end_date)
            )
        if self.format(end_date) > self.db.max_date():
            return abort(404)
        return "{}{}".format(
            request.url_root.strip('/'),
            url_for('releases.json', page=page)
            )

    def prepare_prev(self, page):
        start_date, end_date = self.decode_page(page)
        end_date = start_date
        start_date = self.format(
            arrow.get(end_date) - timedelta(days=1)
            )
        if start_date < self.db.min_date():
            return ()
        page = self.encode_page(start_date, end_date)
        return "{}{}".format(
            request.url_root.strip('/'),
            url_for('releases.json', page=page)
            )