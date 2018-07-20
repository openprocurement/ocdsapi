import pytest
from .base import storage, app
from werkzeug.exceptions import NotFound


@pytest.mark.skip
def test_validate_args(release, client):
    with client.get('/api/release.json?ocid=spam'):
        assert release._validate_args() == {'releaseID': None, 'ocid': 'spam'}
    with client.get('/api/release.json?ocid=spam&releaseID=spam'):
        assert release._validate_args() == {'releaseID': 'spam', 'ocid': 'spam'}
    with client.get('/release.json') as response:
        assert response.status_code == 404

def test_get(client, storage):
    with client.get('/api/release.json?releaseID=test_id') as response:
        assert response.json == storage.get_id('test_id')
    with client.get('/api/release.json?ocid=test_ocid') as response:
        assert response.json == storage.get_ocid('test_ocid')
    with client.get('/release.json') as response:
        assert response.status_code == 404

def test_prepare_response(client, storage):
    with client.get('/api/releases.json?idsOnly=True') as response:
        assert response.json['releases'] == [['spam_id', 'spam_ocid']]
    with client.get('/api/releases.json') as response:
        assert response.json['releases'] == [
            'http://localhost/api/release.json?releaseID=spam_id'
        ]
