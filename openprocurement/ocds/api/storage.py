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

    def __init__(self, config):
        server = couchdb.Server("http://{}:{}".format(config.get("host"),
                                                      config.get("port")))
        db_name = config.get('name', None)
        if db_name in server:
            self.db = server[db_name]
        else:
            self.db = server.create(db_name)
        ViewDefinition.sync_many(self.db, [releases_ocid,
                                           releases_id,
                                           releases_date_id,
                                           releases_date_ocid])

    def get_by_id(self, id):
        return filter_id_rev(self.db.view('releases/by_id', key=id, include_docs=True).rows[0].get('doc'))

    def get_by_ocid(self, ocid):
        return filter_id_rev(self.db.view('releases/by_ocid', key=ocid, include_docs=True).rows[0].get('doc'))

    def get_sorted_by_date(self):
        return self.db.iterview('releases/by_date', 1000, include_docs=True)

    def get_dates(self):
        start_date = next(iter(
            self.db.view('releases/by_date',
                         limit=1).rows
        )).get('key')
        end_date = next(iter(
            self.db.view('releases/by_date',
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
