import pytest
import couchdb
from iso8601 import parse_date
from datetime import timedelta
from openprocurement.ocds.api.storage import (
    ReleaseStorage
)
from openprocurement.ocds.api.app import (
    create_app,
    REGISTRY
)

test_doc = {
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


test_config = {
    "host": "127.0.0.1",
    "port": "5984",
    "name": "test",
    "api_url": "http://127.0.0.1:5000"
}
coudb_url = 'http://{}:{}'.format(test_config.get("host"),
                                  test_config.get("port"))
db_name = test_config.get("name")
SERVER = couchdb.Server(coudb_url)


@pytest.fixture(scope='function')
def db(request):
    def delete():
        del SERVER[db_name]

    if db_name in SERVER:
        delete()
    SERVER.create(db_name)
    request.addfinalizer(delete)


@pytest.fixture(scope='function')
def storage(request):
    storage = ReleaseStorage(test_config)
    REGISTRY.update({"storage": storage})
    storage.db.save(test_doc)
    return storage


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app


def test_app(db, storage, client):
    # Release.json
    res = client.get(
        "{}/release.json?id={}".format(test_config['api_url'], test_doc['id']))
    assert '_id' not in res.json
    assert '_rev' not in res.json
    assert res.status_code == 200
    res = client.get(
        "{}/release.json?ocid={}".format(test_config['api_url'], test_doc['ocid']))
    assert '_id' not in res.json
    assert '_rev' not in res.json
    assert res.status_code == 200
    res = client.get(
        "{}/release.json?id={}".format(test_config['api_url'], "Non existing id"))
    assert res.status_code == 404
    res = client.get(
        "{}/release.json?ocid={}".format(test_config['api_url'], "Non existing ocid"))
    assert res.status_code == 404
    res = client.get(
        "{}/release.json?id={}&packageURL=True".format(test_config['api_url'], test_doc['id']))
    assert res.status_code == 200
    assert len(res.json.keys()) == 1
    assert "package_url" in res.json
    res = client.get(
        "{}/release.json?ocid={}&packageURL=True".format(test_config['api_url'], test_doc['ocid']))
    assert res.status_code == 200
    assert len(res.json.keys()) == 1
    assert "package_url" in res.json
    res = client.get(
        "{}/release.json".format(test_config['api_url']))
    assert "error" in res.json
    assert res.json["error"] == "ReleaseID is required"
    # Releases.json
    res = client.get("{}/releases.json".format(test_config['api_url']))
    assert res
    assert res.status_code == 200
    assert "links" in res.json
    assert "releases" in res.json['links']
    assert type(res.json['links']['releases']) == list
    assert res.json['links']['releases'][0] == "{}/release.json?id={}".format(test_config['api_url'],
                                                                              test_doc['id'])
    assert "next" in res.json['links']
    next_url = res.json['links']['next']
    start_for_url = (parse_date(test_doc['date']) + timedelta(days=1)
                     ).isoformat().split("T")[0]
    end_for_url = (parse_date(test_doc['date']) + timedelta(days=2)
                   ).isoformat().split("T")[0]
    assert next_url == "{}/releases.json?start_date={}&end_date={}".format(
        test_config['api_url'], start_for_url, end_for_url)
    res = client.get("{}/releases.json?start_date={}&end_date={}".format(test_config['api_url'],
                                                                         "2017-01-02", "2017-01-03"))
    assert "error" in res.json
    assert res.json['error'] == "You have reached maximum date"
    end_for_package = (parse_date(test_doc['date']) + timedelta(days=1)
                       ).isoformat().split("T")[0]
    res = client.get("{}/releases.json?start_date={}&end_date={}".format(test_config['api_url'],
                                                                         test_doc["date"],
                                                                         end_for_package))
    assert res.status_code == 200
    assert "links" in res.json
    assert "releases" in res.json['links']
    assert type(res.json['links']['releases']) == list
    res = client.get("{}/releases.json?page=1".format(test_config['api_url']))
    assert res.status_code == 200
    assert "links" in res.json
    assert "releases" in res.json['links']
    assert type(res.json['links']['releases']) == list
    res = client.get("{}/releases.json?page=2".format(test_config['api_url']))
    assert "error" in res.json
    assert res.json['error'] == "Page does not exist"
    # Record.json
    res = client.get("{}/record.json".format(test_config['api_url']))
    assert "error" in res.json
    assert res.json["error"] == 'You must provide OCID'
    res = client.get(
        "{}/record.json?ocid={}".format(test_config['api_url'], test_doc["ocid"]))
    assert res
    assert res.status_code == 200
    for key in ["compiledRelease", "releases", "ocid"]:
        assert key in res.json
    # Records.json
    res = client.get("{}/records.json".format(test_config['api_url']))
    assert res
    assert res.status_code == 200
    assert "links" in res.json
    assert "records" in res.json['links']
    assert type(res.json['links']['records']) == list
    assert res.json['links']['records'][0] == "{}/record.json?ocid={}".format(test_config['api_url'],
                                                                            test_doc['ocid'])
    assert "next" in res.json['links']
    next_url = res.json['links']['next']
    start_for_url = (parse_date(test_doc['date']) + timedelta(days=1)
                     ).isoformat().split("T")[0]
    end_for_url = (parse_date(test_doc['date']) + timedelta(days=2)
                   ).isoformat().split("T")[0]
    assert next_url == "{}/records.json?start_date={}&end_date={}".format(
        test_config['api_url'], start_for_url, end_for_url)
    res = client.get("{}/records.json?start_date={}&end_date={}".format(test_config['api_url'],
                                                                        "2017-01-02", "2017-01-03"))
    assert "error" in res.json
    assert res.json['error'] == "You have reached maximum date"
    end_for_package = (parse_date(test_doc['date']) + timedelta(days=1)
                       ).isoformat().split("T")[0]
    res = client.get("{}/records.json?start_date={}&end_date={}".format(test_config['api_url'],
                                                                        test_doc["date"],
                                                                        end_for_package))
    assert res.status_code == 200
    assert "links" in res.json
    assert "records" in res.json['links']
    assert type(res.json['links']['records']) == list
    res = client.get("{}/records.json?page=1".format(test_config['api_url']))
    assert res.status_code == 200
    assert "links" in res.json
    assert "records" in res.json['links']
    assert type(res.json['links']['records']) == list
    res = client.get("{}/records.json?page=2".format(test_config['api_url']))
    assert "error" in res.json
    assert res.json['error'] == "Page does not exist"
