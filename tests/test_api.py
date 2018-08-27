from .base import app, storage, db, test_docs


def test_get_id_rev(db, storage, client):

    with client.get(
        "/api/release.json?releaseID={}".format(test_docs[0]['id'])) as resp:
        assert '_id' not in resp.json
        assert '_rev' not in resp.json
        assert resp.status_code == 200


def test_get_invalid_id(db, storage, client):
    with client.get("/api/release.json?releaseID=invalid") as res:
        assert res.status_code == 404
        assert 'The requested URL was not found on the server' in res.json['message']
    with client.get("/api/release.json") as res:
        assert res.status_code == 400
        assert res.json['message'] == {
            'releaseID': 'Missing required parameter in the JSON body or the post body or the query string'
            }


