import pytest
from tests.test_api import app, storage
from werkzeug.exceptions import NotFound
from munch import munchify


def test_get(client, storage):
    with client.get('/record.json?ocid=test_ocid') as response:
        assert response.json['releases'][0] == storage.get_ocid('test_ocid')
    with client.get('/record.json?ocid=') as response:
        assert response.status_code == 404

def test_prepare_response(client, storage):
    with client.get('/records.json?idsOnly=True') as response:
        result = response.json
        assert result['records'] == [['spam_id', 'spam_ocid']]
    with client.get('/records.json') as response:
        result = response.json
        assert result['records'] == [
            'http://localhost/record.json?ocid=spam_ocid'
        ]
