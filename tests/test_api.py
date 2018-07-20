from .base import app, storage, db, test_docs


def test_application(db, storage, client):
    # res = client.get("/releases.json")
    # import pdb;pdb.set_trace()
    # assert res.status_code == 200
    # Release.json
    res = client.get(
        "/api/release.json?releaseID={}".format(test_docs[0]['id']))
    assert '_id' not in res.json
    assert '_rev' not in res.json
    assert res.status_code == 200

    # res = client.get(
    #     "/release.json?ocid={}".format(test_doc['ocid'])
    #     )
    # assert '_id' not in res.json
    # assert '_rev' not in res.json
    # assert res.status_code == 200
    res = client.get("/api/release.json?releaseID=invalid")
    # import pdb;pdb.set_trace()
    assert res.status_code == 404

    res = client.get("/api/release.json")
    # assert "message" in res.json
    assert res.status_code == 404
    # assert res.json["message"] == {
    #     "releaseID": "Provide valid releaseID"
    # }
    # Releases.json
    # res = client.get("/releases.json")
    # assert res.status_code == 200
    # assert "links" in res.json
    # assert "releases" in res.json
    # assert type(res.json['releases']) == list
    # assert res.json['releases'][0] == "/release.json?id={}".format(test_doc['id'])
    # assert "next" in res.json['links']
