from .base import app, storage, db, test_docs


def test_get_id_rev(db, storage, client):

    with client.get(
        "/api/release.json?releaseID={}".format(test_docs[0]['id'])) as resp:
        assert '_id' not in resp.json
        assert '_rev' not in resp.json
        assert resp.status_code == 200


def test_get_ocid_rev(db, storage, client):
    with client.get( "/api/release.json?ocid={}".format(test_docs[0]['ocid'])) as resp:
        assert '_id' not in resp.json
        assert '_rev' not in resp.json
        assert resp.status_code == 200


def test_get_invalid_id(db, storage, client):
    with client.get("/api/release.json?releaseID=invalid") as res:
        assert res.status_code == 404
    with client.get("/api/release.json") as res:
        assert res.status_code == 404


def test_get_both_api_ocid(db, storage, client):
    query = "releaseID={}&ocid={}".format(
        test_docs[0]['id'],
        test_docs[0]['ocid']
    )
    with client.get("/api/release.json?{}".format(query)) as res:
        assert res.status_code == 404
