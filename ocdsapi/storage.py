""" storage.py - couchdb wrapper """
import logging
import arrow
import couchdb
from couchdb.design import ViewDefinition
from iso8601 import parse_date
from .utils import get_or_create_db, prepare_responce_doc


LOGGER = logging.getLogger("ocdsapi")


DATEMODIFIED = ViewDefinition(
    'releases', 'datemodified_filter',
    map_fun=u"""function(doc) {emit(doc._id, doc.date);}"""
)

OCID = ViewDefinition(
    'releases', 'id_index',
    map_fun=u"""function(doc) {emit([doc._id, doc.ocid], doc.date);}"""
)

ID = ViewDefinition(
    'releases', 'date_index',
    map_fun=u"""function(doc) {emit([doc.date, doc._id], doc.ocid);}"""
)


class ReleaseStorage(object):

    def __init__(self, host_url, db_name):
        server = couchdb.Server(host_url)
        self.db = get_or_create_db(server, db_name)

        ViewDefinition.sync_many(self.db, [OCID, ID, DATEMODIFIED])
        LOGGER.info("Starting storage: {}".format(
            self.db.info()
        ))

    def _by_id(self, startkey, endkey):
        responce = self.db.view(
            'releases/id_index',
            startkey=startkey,
            endkey=endkey,
            include_docs=True,
            limit=1,
            )
        if responce.rows:
            for row in responce.rows:
                doc = row.get('doc')
                if doc:
                    yield prepare_responce_doc(doc)
        raise StopIteration

    def get_id(self, id_):
        startkey = (id_, '')
        endkey = (id_, 'xxxxxxxxxxx')
        for release in self._by_id(startkey, endkey):
            if release:
                return release

    def get_ocid(self, ocid):
        startkey = ('', ocid)
        endkey = ('x' * 33, ocid)
        return [
            doc for doc in
            self._by_id(startkey, endkey)
        ]

    def _by_date(self, **kw):
        for item in self.db.view(
                'releases/date_index',
                **kw
                ):
            key = item.get('key')
            if key:
                return arrow.get(key[0]).format("YYYY-MM-DD")

    def min_date(self):
        return self._by_date(
            limit=1,
            )

    def max_date(self):
        return self._by_date(
            limit=1,
            descending=True,
            )

    def get_window(self):
        return (self.min_date(), self.max_date())

    def _by_limit(
            self, start_key, view_limit=101,
            include_docs=False, **kw
    ):
        key = parse_date(start_key).isoformat() if start_key else ""
        if key:
            kw['startkey'] = (key, "")
        return self.db.view(
            'releases/date_index',
            limit=view_limit,
            include_docs=include_docs,
            **kw
        )

    def page(self, start_date, include_docs=False, **kw):
        resp = self._by_limit(
            start_date, include_docs=include_docs, **kw
        )
        if not include_docs:
            if resp and resp.rows:
                data = [
                    {
                        'id': item.id,
                        'date': item.key[0],
                        'ocid': item.value
                    }
                    for item in resp
                ]
                last = data[-1][1]
                return last, data[:-1]
        else:
            data = [
                {
                    'id': item.id,
                    'date': item.key[0],
                    'ocid': item.value,
                    'doc': prepare_responce_doc(item.doc)
                }
                for item in resp
            ]
            if data:
                last = data[-1]
                return last, data[:-1]
        return ("", "")

    def _inside(self, start_date, end_date):
        return self.db.view(
            'releases/date_index',
            startkey=(parse_date(start_date).isoformat(), ""),
            endkey=(parse_date(end_date).isoformat(), ""),
            )

    def ids_inside(self, start_date="", end_date=""):
        return [
            item.get('key')[1]
            if item else ""
            for item in self._inside(start_date, end_date)
        ]

    def ocids_inside(self, start_date, end_date):
        return [
            row.value
            for row in self._inside(start_date, end_date)
        ]
