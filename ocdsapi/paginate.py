import arrow
from datetime import timedelta
from urllib.parse import urljoin
from flask import current_app as app
from flask import request, abort, url_for


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

    @classmethod
    def format(self, date):
        return date.format("YYYY-MM-DD")
    
    def prepare_initial_offset(self):
        start_date = self._get_min()
        return (
            self.format(start_date),
            self.format(start_date+timedelta(days=1))
            )

    def get_url(self, page):
        return urljoin(
            request.url_root,
            url_for('releases.json', page=page)
        )

    def next_page(self, start_date):
        end_date = self.format(
            arrow.get(start_date) + timedelta(days=1)
            )
        if end_date > self.db.max_date():
            start_date = end_date = self.db.max_date()
        return self.encode_page(
            start_date,
            end_date
            )

    def prev_page(self, end_date):
        start_date = self.format(
            arrow.get(end_date) - timedelta(days=1)
            )
        if start_date < self.db.min_date():
            return self.encode_page(
                *self.prepare_initial_offset()
            )
        return self.encode_page(start_date, end_date)

    def next_url(self, start_date):
        try:
            return self.get_url(
                self.next_page(start_date)
            )
        except ValueError:
            return abort(404)
        
    def prev_url(self, end_date):
        return self.get_url(
            self.prev_page(end_date)
        )
