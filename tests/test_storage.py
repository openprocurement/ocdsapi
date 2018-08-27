import pytest
import couchdb
from ocdsapi.storage import (
    ReleaseStorage
)
from copy import deepcopy

test_release = {
   "_id": "test_id",
   "_rev": "1-f9da923910334137a23e6f16af78d438",
   "language": "uk",
   "ocid": "test_ocid",
   "initiationType": "tender",
   "date": "2017-01-01",
   "tag": [
       "tender"
   ],
   "tender": {
       "procurementMethod": "limited",
       "status": "complete",
       "id": "test_id"
   },
   "id": "test_id",
   "$schema": ""
}


DB_HOST = "http://admin:admin@127.0.0.1:5984"
DB_NAME = "test"

SERVER = couchdb.Server(DB_HOST)


@pytest.fixture(scope='function')
def db(request):
    def delete():
        del SERVER[DB_NAME]

    if DB_NAME in SERVER:
        delete()
    SERVER.create(DB_NAME)
    request.addfinalizer(delete)


@pytest.fixture(scope='function')
def storage(request):
    storage = ReleaseStorage(DB_HOST, DB_NAME)
    try:
        storage.db.save(test_release)
    except couchdb.http.ResourceConflict:
        pass
    except:
        raise
    return storage


class TestStorage(object):

    #@pytest.mark.parametrize('storage', [ReleaseStorage])
    def test_create(self, storage):
        if DB_NAME in SERVER:
            del SERVER[DB_NAME]
        storage = ReleaseStorage(DB_HOST, DB_NAME)
        assert DB_NAME in SERVER

    def test_get_by_id(self, db, storage):
        release = storage.get_id(test_release.get("id"))
        assert release
        assert "_id" not in release
        assert "_rev" not in release

    def test_get_by_ocid(self, db, storage):
        release = storage.get_ocid(test_release.get("ocid"))[0]
        assert release
        assert release['tender'] == test_release['tender']
        assert "_id" not in release
        assert "_rev" not in release

    # def test_get_sorted_by_date(self, db, storage):
    #     test_release['date'] = '2017-01-02'
    #     test_release['_id'] = 'test_id1'
    #     storage.db.save(test_release)
    #     for item, id in zip(storage.get_sorted_by_date(), ['test_id', "test_id1"]):
    #         assert item.value == id

    def test_get_dates(self, db, storage):
        dates = storage.get_window()
        assert dates[0] == test_release['date']
        small_date = '2016-01-01'
        test_release['date'] = small_date
        test_release['_id'] = 'test1'
        storage.db.save(test_release)
        dates = storage.get_window()
        assert dates[0] == small_date

    def test_get_all_ids_between_dates(self, db, storage):
        date1 = '2016-01-01'
        date2 = '2016-02-01'
        release1 = deepcopy(test_release)
        release1['date'] = date1
        release1['_id'] = 'test1'
        storage.db.save(release1)
        release2 = deepcopy(test_release)
        release2['date'] = date2
        release2['_id'] = 'test2'
        storage.db.save(release2)
        result = list(storage.ids_inside(date1, date2))
        assert len(result) == 1
        assert result[0] == 'test2'

    def test_get_all_ocids_between_dates(self, db, storage):
        date1 = '2016-01-01'
        date2 = '2016-02-01'
        release1 = deepcopy(test_release)
        release1['date'] = date1
        release1['_id'] = 'test1'
        release1['ocid'] = 'ocid1'
        storage.db.save(release1)
        release2 = deepcopy(test_release)
        release2['date'] = date2
        release2['_id'] = 'test2'
        release2['ocid'] = 'ocid2'
        storage.db.save(release2)
        result = list(storage.ocids_inside(date1, date2))
        assert len(result) == 1
        assert result[0] == 'ocid2'
