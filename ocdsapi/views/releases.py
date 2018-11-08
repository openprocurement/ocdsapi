from cornice.resource import resource, view
from sqlalchemy import tuple_
from itertools import chain
from paginate_sqlalchemy import SqlalchemyOrmPage
from ocdsapi.models import Release
from ocdsapi.validation import validate_release_bulk, validate_release_id

YES = frozenset(('true', '1', 'y', 'yes', 't'))

@resource(
    name='releases.json',
    path='/releases.json',
    description=""
)
class ReleasesResource:
    def __init__(self, request, context=None):
        self.request = request
        self.page_size = request.registry.page_size

    @view(validators=(validate_release_bulk))
    def post(self):
        session = self.request.dbsession
        releases = self.request.validated['releases']
        query = (session
                 .query(Release.release_id)
                 .filter(Release.release_id.in_(tuple(releases.keys()))))
        existing = set(chain(*query.all()))
        result = {}
        for release_id in releases.keys():
            if release_id in existing:
                result[release_id] = {
                    'status': 'error',
                    'description': "{} already exists".format(release_id)
                }
            else:
                release_raw = releases.get(release_id)
                release = Release(
                    release_id=release_raw['id'],
                    ocid=release_raw['ocid'],
                    date=release_raw.get('date'),
                    value=release_raw
                )

                try:
                    session.add(release)
                    result[release_id] = {
                        "status": "ok",
                        "description": 'ok'
                    }
                except Exception as e:
                    result[release_id] = {
                        'status': 'error',
                        'description': e.message
                    }

        return result


    @view()
    def get(self):
        page_number_requested = self.request.params.get('page') or 1
        ids_only = self.request.params.get('idsOnly', '')\
                   and self.request.params.get('idsOnly').lower() in YES
        if ids_only:
            pager = SqlalchemyOrmPage(
                self.request.dbsession.query(
                    Release.release_id, Release.ocid, Release.date
                ),
                page=int(page_number_requested),
                items_per_page=self.page_size
            )
        else:
            pager = SqlalchemyOrmPage(
                self.request.dbsession.query(Release),
                page=int(page_number_requested),
                items_per_page=self.page_size
            )
        return self.request.release_package(pager, ids_only)


@resource(
    name='release.json',
    path='/release.json',
    description=''
)
class ReleaseResource:

    def __init__(self, request, context=None):
        self.request = request

    @view(validators=(validate_release_id))
    def get(self):
        id_ = self.request.validated['release_id']
        release = self.request.dbsession.query(Release).filter(Release.release_id==id_).first()
        return release.value