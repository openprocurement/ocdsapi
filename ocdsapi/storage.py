import arrow
import couchdb
from iso8601 import parse_date
from couchdb.design import ViewDefinition
from ocdsapi.utils import prepare_responce_doc


releases_ocid = ViewDefinition(
    'releases', 'id_index',
    map_fun=u"""function(doc) {emit([doc._id, doc.ocid], doc.date);}"""
)

releases_id = ViewDefinition(
    'releases', 'date_index',
    map_fun=u"""function(doc) {emit([doc.date, doc._id], doc.ocid);}"""
)


class ReleaseStorage(object):

    def __init__(self, host, port, db_name):
        server = couchdb.Server("http://{}:{}".format(host,
                                                      port))
        if db_name in server:
            self.db = server[db_name]
        else:
            self.db = server.create(db_name)
        ViewDefinition.sync_many(self.db, [releases_ocid,
                                           releases_id,])

    def _by_id(self, _filter):
        
        responce = self.db.view(
            'releases/id_index',
            startkey=_filter,
            include_docs=True,
            limit=1
            )
        if responce.rows:
            for row in responce.rows:
                doc = row.get('doc')
                if doc:
                    return prepare_responce_doc(doc)
        return ""

    def get_id(self, id):
        return self._by_id((id, ""))

    def get_ocid(self, ocid):
        return self._by_id(("", ocid))

    def _by_date(self, **kw):
        for item in self.db.view(
                'releases/date_index',
                **kw
                ):
            key = item.get('key')
            if key:
                return arrow.get(key[0]).format("YYYY-MM-DD")
    
    def min_date(self):
        return self._by_date(limit=1)
        
    def max_date(self):
        return self._by_date(
            limit=1,
            descending=True
            )

    def get_window(self):
        return (self.min_date(), self.max_date())
    
    def _inside(self, start_date, end_date):
        return self.db.iterview(
            'releases/date_index',
            1000,
            startkey=(parse_date(start_date).isoformat(), ""),
            endkey=(parse_date(end_date).isoformat(), ""),
            include_docs=True
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