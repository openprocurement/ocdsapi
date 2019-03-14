from sqlalchemy import or_, and_, func, cast, TIMESTAMP
from dateutil import parser

import base64


class Pager:

    def __init__(self, request, model, limit=100):
        self.model = model
        self.request = request
        self.session = request.dbsession
        self.limit = limit
        self.base = self._query()

        self.directions = {'next': self._next, 'prev': self._prev}
        self.start_key = ''
        self.timestamp = ''
        self.direction = ''

        page = self.request.params.get('page', '')
        if page:
            self.add_pivot(page)

    def _query(self):
        return self.session.query(self.model).order_by(
               self.model.timestamp.asc()
               )

    def _next(self, timestamp, start_key):
        ands = and_(self.model.timestamp == timestamp, self.model.id > start_key).self_group()
        return self.session.query(self.model).order_by(
                self.model.timestamp.asc()
            ).filter(
            or_(
                self.model.timestamp > timestamp,
                ands
            ))

    def _prev(self, timestamp, start_key):
        ands = and_(self.model.timestamp == timestamp, self.model.id < start_key).self_group()
        return self.session.query(self.model).order_by(
                self.model.timestamp.desc()
            ).filter(
            or_(
                self.model.timestamp < timestamp,
                ands
            ))
        # return self.session.query(self.model).filter((self.model.timestamp < timestamp) | (self.model.timestamp == timestamp & self.model.id < start_key)).order_by(self.model.timestamp.desc())

    def _wrap_token(self, ident, timestamp, direction='next'):
        if not isinstance(timestamp, str):
            timestamp = timestamp.isoformat()
        raw_string = '@'.join((ident, timestamp, direction))
        return base64.urlsafe_b64encode(raw_string.encode('ascii')).decode('ascii')

    def add_pivot(self, token):
        try:
            raw_string = base64.urlsafe_b64decode(
                token.encode('ascii')
            )
            self.start_key, self.timestamp, self.direction = raw_string.decode('ascii').split('@')
            self.timestamp = parser.parse(self.timestamp)
        except Exception as e:
            self.request.error.add('querystring', 'token', 'invalid')
            raise e
        self.base = self.directions[self.direction](self.timestamp, self.start_key)

    def run(self):
        items = self.base.limit(self.limit).all()
        if items:
            last = items[-1]
            first = items[0]
            if self.direction and self.direction == 'prev':
                next_page = self._wrap_token(first.id, first.timestamp)
                prev_page = self._wrap_token(last.id, last.timestamp, 'prev')
            else:
                next_page = self._wrap_token(last.id, last.timestamp)
                prev_page = self._wrap_token(first.id, first.timestamp, 'prev')

            # prev_page = self._wrap_token(first.id, first.timestamp, 'prev')

            return items, next_page, prev_page
        return (
            [],
            self._wrap_token(self.start_key, self.timestamp),
            self._wrap_token(self.start_key, self.timestamp, 'prev')
            )

