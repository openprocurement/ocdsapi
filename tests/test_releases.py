import pytest
from .base import storage, app, test_docs
from werkzeug.exceptions import NotFound


def test_get(client, storage):
    with client.get('/api/release.json?releaseID=test_id') as response:
        assert response.json == storage.get_id('test_id')
    with client.get('/release.json') as response:
        assert response.status_code == 404


def test_prepare_response(client, storage):
    with client.get('/api/releases.json?idsOnly=True') as response:
        assert response.json['releases'] == [{"id": 'spam_id', "ocid": 'spam_ocid'}]
    with client.get('/api/releases.json') as response:
        release = response.json['releases']
        assert release[0]['ocid'] == test_docs[1]['ocid']
        assert release[0]['date'] == test_docs[1]['date']
