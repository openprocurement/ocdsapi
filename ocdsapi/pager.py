class Pager:
    def __init__(self, request, model, limit=100):
        self.model = model
        self.request = request
        self.session = request.dbsession
        self.limit = limit
        self.base = self.query()
        self.pivot = ()

    def query(self):
        return self.session.query(self.model).order_by(
               self.model.timestamp.asc(), self.model.id.asc()
               )

    def _wrap_token(self, ident, timestamp, direction='forward'):
        if not isinstance(timestamp, str):
            timestamp = timestamp.isoformat()
        raw_string = '@'.join((ident, timestamp, direction))
        return base64.urlsafe_b64encode(raw_string.encode('ascii')).decode('ascii')

    def add_pivot(self, token):
        try:
            raw_string = base64.urlsafe_b64decode(
                token.encode('ascii')
            )
            start_key, timestamp, d = raw_string.decode('ascii').split('@')
            self.pivot = (start_key, timestamp)
        except Exception as e:
            self.request.error.add('querystring', 'token', 'token has expired')
            raise e
        direction = DIRECTIONS[d]
        timestamp = cast(timestamp, TIMESTAMP)
        self.base = self.query().filter(
            or_(
                direction(self.model.modified_at, timestamp),
                and_(
                    self.model.modified_at == timestamp,
                    direction(self.model.id, start_key),
                )
            )).filter(
                self.model.modified_at < func.current_timestamp()
            )

    def run(self):
        items = self.base.limit(self.limit).all()
        if items:
            last = items[-1]
            first = items[0]
            next_page = self._wrap_token(last.id, last.modified_at)
            prev_page = self._wrap_token(first.id, first.modified_at, 'backward')
            return items, next_page, prev_page
        start_id, timestamp = self.pivot
        return (
            [],
            self._wrap_token(start_id, timestamp),
            self._wrap_token(start_id, timestamp, 'backward')
            )

