from ocdsapi.base import BaseCollectionResource
from tests.test_api import app, storage
import pytest

@pytest.fixture
def resource():
    return BaseCollectionResource()

def test_prepare_next_url(resource, app):
    resource.resource = 'releases.json'
    with app.app_context(), app.test_request_context():
        url_ascending = resource.prepare_next_url({'offset': 0})
        assert url_ascending == '/api/releases.json?page=0'
    with app.app_context(), app.test_request_context():
        url_descending = resource.prepare_next_url({'offset': 0, 'descending': True})
        assert url_descending == '/api/releases.json?page=0&descending=True'

def test_prepare_response(client, storage):
    with client.get('/api/releases.json') as response:
        result = response.json
        assert result['links']['next'] == 'http://localhost/api/releases.json?page=2017-01-01'
    with client.get('/api/releases.json?page=2017-01-01&descending=True') as response:
        result = response.json
        assert result['links']['next'] == 'http://localhost/api/releases.json?page=2017-01-01&descending=True'
        assert result['links']['prev'] == 'http://localhost/api/releases.json?page=2017-01-01'
