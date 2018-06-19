import pytest
from ocdsapi.releases import ReleaseResource
from tests.test_api import app, storage
from werkzeug.exceptions import NotFound

@pytest.fixture
def release(storage):
    return ReleaseResource(db=storage)

def test_validate_args(release, client):
    with client.get('/release.json?ocid=spam'):
        assert release._validate_args() == {'releaseID': None, 'ocid': 'spam'}
    with client.get('/release.json?ocid=spam&releaseID=spam'):
        assert release._validate_args() == {'releaseID': 'spam', 'ocid': 'spam'}
    with client.get('/release.json') as response:
        assert response.status_code == 404

def test_get(client, storage):
    with client.get('/release.json?releaseID=test_id') as response:
        assert response.json == storage.get_id('test_id')
    with client.get('/release.json?ocid=test_ocid') as response:
        assert response.json == storage.get_ocid('test_ocid')
    with client.get('/release.json') as response:
        assert response.status_code == 404

def test_prepare_response(client, storage):
    with client.get('/releases.json?idsOnly=True') as response:
        assert response.json['releases'] == [['spam_id', 'spam_ocid']]
    with client.get('/releases.json') as response:
        assert response.json['releases'] == [
            'http://localhost/release.json?releaseID=spam_id'
        ]
