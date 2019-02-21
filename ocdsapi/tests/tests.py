import unittest
import os
import os.path
import uuid
from datetime import datetime

from pyramid import testing

import transaction
import webtest

from ocdsapi.models import Release, Record


DIR = os.path.dirname(os.path.abspath(__file__))
PG_URL = os.environ.get(
    'PG_URL',
    'postgresql+psycopg2cffi://postgres:admin@127.0.0.1:5432/testing'
)


class BaseTest(unittest.TestCase):

    def setUp(self):
        """ set up test enviroment """
        self.config = testing.setUp(settings={
            'sqlalchemy.url': PG_URL
        })
        self.config.include('ocdsapi.models')
        settings = self.config.get_settings()

        from ocdsapi.models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        self.session = get_tm_session(session_factory, transaction.manager)

        # Shortcuts
        self.eq = self.assertEqual
        self.ok = self.assertTrue
        self.nok = self.assertFalse
        self.init_database()
        self.init_application()

    def init_application(self):
        from ocdsapi.app import main
        self.app = webtest.TestApp(main({}, **{
            'api.publisher': os.path.join(DIR, 'data/publisher.yml'),
            'api.schema': os.path.join(DIR, 'data/schema.json'),
            'sqlalchemy.url': PG_URL,
            'api.tokens': 'secret'
        }))

    def init_database(self):
        from ocdsapi.models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from ocdsapi.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class TestHealth(BaseTest):

    def test_health(self):
        resp = self.app.get("/api/health")
        self.eq(resp.status, '200 OK')
        self.eq(resp.json, {"status": "ok"})


class TestSwagger(BaseTest):

    def test_swagger(self):
        resp = self.app.get("/api/swagger.json")
        self.eq(resp.status, '200 OK')
        info = resp.json['info']
        self.nok(set(info.keys()).difference([
            'title', 'description', 'version', 'termsOfService']))
        paths = set(['/records.json', '/record.json', '/releases.json', '/release.json'])
        self.eq(set(resp.json['paths']), paths)
        for path in paths:
            info = resp.json['paths'][path]
            self.eq(list(info.keys()), ['get'])


class TestNotFount(BaseTest):

    def test_health(self):
        resp = self.app.get("/api/missing", status=404)
        self.eq(resp.status, '404 Not Found')
        self.eq(resp.json, {"status": "Not Found"})


class TestReleasesResourceRead(BaseTest):

    def test_get_releases_on_empty_database(self):
        resp = self.app.get('/api/releases.json')
        self.eq(resp.status, '200 OK')
        json_body = resp.json
        self.eq(json_body.pop('releases'), [])
        self.nok(set(json_body.keys()).difference(
            set(['publisher',
                 'license',
                 'version',
                 'extensions',
                 'links',
                 'publishedDate',
                 'uri',
                 'publicationPolicy'
                 ])
        ))

    def test_get_simple_page(self):
        models = [
            Release(
                release_id=uuid.uuid4().hex,
                ocid='ocid-{}'.format(index),
                value={"id": str(index)*10}
            )
            for index in range(10)
        ]
        for model in models:
            self.session.add(model)
        resp = self.app.get('/api/releases.json')
        self.eq(resp.status, '200 OK')
        releases = resp.json['releases']
        self.nok(set((r['ocid'] for r in releases)).difference(
            set((m.ocid for m in models))
            ))
        self.nok(set((r['release_id'] for r in releases)).difference(
            set((m.release_id for m in models))
            ))

    def test_get_ids_only(self):
        models = [
            Release(
                release_id=uuid.uuid4().hex,
                ocid='ocid-{}'.format(index),
                date=datetime.now().isoformat(),
                value={"id": str(index)*10}
            )
            for index in range(10)
        ]
        for model in models:
            self.session.add(model)
        resp = self.app.get('/api/releases.json', params={"idsOnly": True})
        self.eq(resp.status, '200 OK')
        releases = resp.json['releases']
        for release in releases:
            self.nok(
                set(release.keys()).difference(
                    set(('id', 'date')))
                )

    def test_get_next_page(self):
        models = [
            Release(
                release_id=uuid.uuid4().hex,
                ocid='ocid-{}'.format(index),
                date=datetime.now().isoformat(),
                value={
                    "id": str(index)*10,
                    'title': str(index),
                    'date': datetime.now().isoformat()
                    }
            )
            for index in range(300)
        ]
        for model in models:
            record = Record(ocid=model.ocid, releases=[model], date=model.date)
            self.session.add(record)
        for model in models:
            self.session.add(model)
        transaction.commit()
        resp = self.app.get('/api/releases.json')
        self.eq(resp.status, '200 OK')
        self.ok('next' in resp.json['links'])

        resp = self.app.get('/api/releases.json', params={"page": 2})
        self.eq(resp.status, '200 OK')
        self.ok('next' in resp.json['links'])
        self.ok('prev' in resp.json['links'])


class TestReleasesCreate(BaseTest):

    def test_create_release_without_token(self):
        resp = self.app.post_json(
                '/api/releases.json',
                {"data": {'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}},
                status=403
                )
        self.eq(resp.status, '403 Forbidden')
        self.eq(resp.json, {
            'status': 'error',
            'description': 'Forbidden'
            })

    def test_validate_releases_bulk_upload_release_body(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json',
                {
                    'data':
                    [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                },
                status=400
                )
        self.eq(resp.status, '400 Bad Request')
        self.eq(resp.json['status'], 'error')
        for error in resp.json['errors']:
            error['location'] = 'body'
            error['name'] = 'releases'
            error['description'] = 'releases data missing'

    def test_validate_releases_bulk_upload_release_not_array(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json',
                {
                    'releases':
                    {'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}
                },
                status=400
                )
        self.eq(resp.status, '400 Bad Request')
        self.eq(resp.json['status'], 'error')
        for error in resp.json['errors']:
            error['location'] = 'body'
            error['name'] = 'releases'
            error['description'] = 'releases data is not an array'

    def test_create_release_success(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        body = resp.json
        for id in body:
            item = body[id]
            self.eq(item['status'], 'ok')


class TestReleaseResource(BaseTest):

    def test_get_release_without_release_id(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        body = resp.json
        for id in body:
            resp = self.app.get('/api/release.json', status=400)
            self.eq(resp.status, '400 Bad Request')
            body = resp.json
            self.eq(body['status'], 'error')
            for error in body['errors']:
                error['location'] = 'querystring'
                error['name'] = 'releaseID'
                error['description'] = 'releaseID is required'

    def test_get_release(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        body = resp.json
        for id in body:
            resp = self.app.get('/api/release.json', params={'releaseID': id})
            self.eq(resp.status, '200 OK')

    def test_get_release_not_found(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.get(
            '/api/release.json',
            params={'releaseID': 'invalid'},
            status=400
            )
        self.eq(resp.status, '400 Bad Request')
        self.eq(resp.json['status'], 'error')
        for error in resp.json['errors']:
            self.eq(error['location'], "querystring")
            self.eq(error['name'], "releaseID")
            self.eq(error['description'], "Release 'invalid' Not Found")


class TestRecordsResource(BaseTest):

    def test_get_records_ids_only(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        resp = self.app.get(
            '/api/records.json',
            params={'ocid': 'ocds-xxxxx', "idsOnly": True}
            )
        self.eq(resp.status, '200 OK')
        records = resp.json['records']
        for record in records:
            self.nok(
                set(record.keys()).difference(
                    set(('id', 'ocid')))
                )

    def test_get_records_page(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        resp = self.app.get('/api/records.json')
        self.eq(resp.status, '200 OK')
        json_body = resp.json
        self.nok(set(json_body.keys()).difference(
            set(['publisher',
                 'license',
                 'version',
                 'extensions',
                 'links',
                 'publishedDate',
                 'uri',
                 'releases',
                 'records',
                 'publicationPolicy'
                 ])
        ))
    def test_get_record_next_page(self):

        transaction.begin()
        models = [
            Release(
                release_id=uuid.uuid4().hex,
                ocid='ocid-{}'.format(index),
                date=datetime.now().isoformat(),
                value={
                    "id": str(index)*10,
                    'title': str(index),
                    'ocid': str(index),
                    'date': datetime.now().isoformat()
                    }
            )
            for index in range(300)
        ]
        for model in models:
            record = Record(ocid=model.ocid, releases=[model], date=model.date)
            #self.session.add(record)
        for model in models:
            self.session.add(model)
        transaction.commit()
        resp = self.app.get('/api/records.json')
        self.eq(resp.status, '200 OK')
        self.ok('next' in resp.json['links'])

        resp = self.app.get('/api/records.json', params={"page": 2})
        self.eq(resp.status, '200 OK')
        self.ok('next' in resp.json['links'])
        self.ok('prev' in resp.json['links'])



class TestRecordResource(BaseTest):

    def test_validate_params_ocid(self):
        resp = self.app.get(
            '/api/record.json',
            status=400
            )
        self.eq(resp.status, '400 Bad Request')
        self.eq(resp.json['status'], 'error')
        for error in resp.json['errors']:
            self.eq(error['location'], 'querystring')
            self.eq(error['name'], 'ocid')
            self.eq(error['description'], 'ocid query argument missing')


    def test_get_record_not_exists(self):
        resp = self.app.get(
            '/api/record.json',
            params={'ocid': 'xxxxxx'},
            status=400
            )
        self.eq(resp.status, '400 Bad Request')
        self.eq(resp.json['status'], 'error')
        for error in resp.json['errors']:
            self.eq(error['location'], 'querystring')
            self.eq(error['name'], 'ocid')
            self.eq(error['description'], 'Record xxxxxx not found')

    def test_get_record_by_ocid(self):
        self.app.authorization = ('Basic', ('secret', ''))
        resp = self.app.post_json(
                '/api/releases.json', {
                        'releases':
                        [{'id': 'x'*10, 'date': '2018-01-01', 'ocid': 'ocds-xxxxx'}]
                    },
                )
        self.eq(resp.status, '200 OK')
        resp = self.app.get('/api/record.json', params={'ocid': 'ocds-xxxxx'})
        self.eq(resp.status, '200 OK')
        json_body = resp.json
        self.nok(set(json_body.keys()).difference(
            set(['publisher',
                 'license',
                 'version',
                 'extensions',
                 'links',
                 'publishedDate',
                 'uri',
                 'releases',
                 'records',
                 'publicationPolicy'
                 ])
        ))
