from sqlalchemy import or_, and_, func, cast, TIMESTAMP

import base64


class Pager:

    def __init__(self, request, model, limit=100):
        self.model = model
        self.request = request
        self.session = request.dbsession
        self.limit = limit
        self.base = self.query()
        self.pivot = ()

        self.directions = {'next': self._next, 'prev': self._prev}

        page = self.request.params.get('page', '')
        if page:
            self.add_pivot(page)

    def query(self):
        return self.session.query(self.model).order_by(
               self.model.timestamp.asc()
               )

    def _next(self, timestamp, start_key):
         return self.query().filter(
            or_(
                self.model.timestamp > timestamp,
                and_(
                    self.model.timestamp == timestamp,
                    self.model.id > start_key,
                )
            )).filter(
                self.model.timestamp < func.current_timestamp()
            )

    def _prev(self, timestamp, start_key):
        return self.query().filter(
            or_(
                self.model.timestamp < timestamp,
                and_(
                    self.model.timestamp == timestamp,
                    self.model.id < start_key,
                )
            ))

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
            start_key, timestamp, direction = raw_string.decode('ascii').split('@')
            self.pivot = (start_key, timestamp)
        except Exception as e:
            self.request.error.add('querystring', 'token', 'token has expired')
            raise e
        timestamp = cast(timestamp, TIMESTAMP)
        self.base = self.directions[direction](timestamp, start_key)

    def run(self):
        items = self.base.limit(self.limit).all()
        if items:
            last = items[-1]
            first = items[0]
            next_page = self._wrap_token(last.id, last.timestamp)
            prev_page = self._wrap_token(first.id, first.timestamp, 'prev')
            return items, next_page, prev_page
        start_id, timestamp = self.pivot
        return (
            [],
            self._wrap_token(start_id, timestamp),
            self._wrap_token(start_id, timestamp, 'prev')
            )

