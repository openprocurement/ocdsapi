import couchdb
from couchdb.design import ViewDefinition
from openprocurement.ocds.api.utils import filter_id_rev


releases_ocid = ViewDefinition(
    'releases', 'by_ocid',
    map_fun=u"""function(doc) {emit(doc.ocid);}"""
)

releases_id = ViewDefinition(
    'releases', 'by_id',
    map_fun=u"""function(doc) {emit(doc._id);}"""
)

releases_date_id = ViewDefinition(
    'releases', 'by_date_id',
    map_fun=u"""function(doc) {emit(doc.date, doc._id);}"""
)

releases_date_ocid = ViewDefinition(
    'releases', 'by_date_ocid',
    map_fun=u"""function(doc) {emit(doc.date, doc.ocid);}"""
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
                                           releases_id,
                                           releases_date_id,
                                           releases_date_ocid])

    def get_by_id(self, id):
        res = self.db.view('releases/by_id', key=id, include_docs=True)
        return filter_id_rev(res.rows[0].get('doc')) if res else None

    def get_by_ocid(self, ocid):
        res = self.db.view('releases/by_ocid', key=ocid, include_docs=True)
        return filter_id_rev(res.rows[0].get('doc')) if res else None

    def get_sorted_by_date(self):
        return self.db.iterview('releases/by_date_id', 1000, include_docs=True)

    def get_dates(self):
        start_date = next(iter(
            self.db.view('releases/by_date_id',
                         limit=1).rows
        )).get('key')
        end_date = next(iter(
            self.db.view('releases/by_date_id',
                         limit=1,
                         descending=True).rows
        )).get('key')
        return start_date.split('T')[0], end_date.split('T')[0]

    def get_all_ids_between_dates(self, start_date, end_date):
        return self.db.iterview('releases/by_date_id',
                                1000,
                                startkey=start_date,
                                endkey=end_date,
                                include_docs=True)

    def get_all_ocids_between_dates(self, start_date, end_date):
        return self.db.iterview('releases/by_date_ocid',
                                1000,
                                startkey=start_date,
                                endkey=end_date,
                                include_docs=True)
