from ocdsapi.base import BaseCollectionResource
from tests.test_api import app
import pytest
import flask

@pytest.fixture
def resource():
    return BaseCollectionResource()

def test_prepare(resource):
    try:
        resource._prepare()
    except Exception as exc:
        assert isinstance(exc, NotImplementedError)

def test_prepare_next_url(resource, app):
    resource.resource = 'releases.json'
    with app.app_context(), app.test_request_context():
        url_ascending = resource.prepare_next_url({'offset': 0})
        assert url_ascending == '/releases.json?page=0'
    with app.app_context(), app.test_request_context():
        url_descending = resource.prepare_next_url({'offset': 0, 'descending': True})
        assert url_descending == '/releases.json?page=0&descending=True'
