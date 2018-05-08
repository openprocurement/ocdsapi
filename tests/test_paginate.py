import pytest
import couchdb
from ocdsapi.paginate import PaginationHelper
from ocdsapi.storage import ReleaseStorage

DB_HOST = "http://admin:admin@127.0.0.1:5984"
DB_NAME = "test"

SERVER = couchdb.Server(DB_HOST)
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
   "id": "test_id"
}

@pytest.fixture(scope='function')
def db(request):
    def delete():
        del SERVER[DB_NAME]

    if DB_NAME in SERVER:
        delete()
    SERVER.create(DB_NAME)
    request.addfinalizer(delete)


@pytest.fixture(scope='function')
def paginator(request):
    storage = ReleaseStorage(DB_HOST, DB_NAME)
    storage.db.save(test_release)

    paginator = PaginationHelper(storage)
    return (storage, paginator)


class TestPaginate(object):

    def test_encode(self, db, paginator):
        _, paginate = paginator
        start = '2016-01-01'
        end = '2016-01-02'
        assert paginate.encode_page(start, end) == '2016-01-01--2016-01-02'

    def test_decode(self,db, paginator):
        _, paginate = paginator
        assert paginate.decode_page('2016-01-01--2016-01-02') ==\
         ['2016-01-01', '2016-01-02']

    def test_initial(self, db, paginator):
        _, paginate = paginator
        start, end = paginate.prepare_initial_offset()
        assert start == '2017-01-01'
        assert end == '2017-01-02'
