from .base import app, storage, db, test_docs


def test_swagger_docs(client, storage):
    with client.get('/api/swagger.json') as responce:
        data = responce.json
        for endpoint in (
            "/api/record.json",
            "/api/records.json",
            "/api/release.json",
            "/api/releases.json"):
            assert endpoint in data['paths']