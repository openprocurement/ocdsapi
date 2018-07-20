import pytest
import couchdb
from ocdsapi.storage import (
    ReleaseStorage
)
from ocdsapi.application import (
    make_paste_application
)


test_docs = [
    {
        "_id": "test_id",
        "language": "uk",
        "ocid": "ocid-xxxx-xxxx",
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
    },
    {
        "_id": "spam_id",
        "ocid": "spam_ocid",
        "date": "2017-01-01",
        "$schema": "",
    }
]
DB_HOST = "http://admin:admin@127.0.0.1:5984"
DB_NAME = "test"
APP = make_paste_application(
    {}, couchdb_url=DB_HOST, couchdb_dbname=DB_NAME
)

@pytest.fixture(scope='function')
def app():
    return APP


@pytest.fixture(scope='function')
def db(request):
    SERVER = couchdb.Server(DB_HOST)
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
        for doc in test_docs:
            storage.db.save(doc)
    except couchdb.http.ResourceConflict:
        pass
    except:
        raise
    return storage
