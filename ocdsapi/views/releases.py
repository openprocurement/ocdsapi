import operator
from logging import getLogger

import ocdsmerge
from cornice.resource import resource, view
from itertools import chain
from paginate_sqlalchemy import SqlalchemyOrmPage
from sqlalchemy import exc
from ocdsapi.models import Release, Record
from ocdsapi.validation import validate_release_bulk, validate_release_id
from ocdsapi.constants import YES
from ocdsapi.utils import wrap_in_release_package, factory
from ocdsapi.events import RecordBatchUpdate


logger = getLogger('ocdsapi')


@resource(
    name='releases.json',
    path='/releases.json',
    description="Due to releases the updates on each contracting process event are supplied on a real-time basis. This feature assists users in receiving notifications about announcing new tenders, conducted awards, making contracts and similar updates. More than one releases may be published during a contracting process. Releases cannot be altered at any point since they are supposed to provide information precisely following each step of contracting cycle.",
    factory=factory
)
class ReleasesResource:
    def __init__(self, request, context=None):

        self.request = request
        self.page_size = request.registry.page_size

    @view(validators=(validate_release_bulk),
          content_type='application/json', permission='create')
    def post(self):
        """ Create new releases """
        session = self.request.dbsession
        releases = self.request.validated['releases']
        query = (session
                 .query(Release.release_id)
                 .filter(Release.release_id.in_(tuple(releases['ok'].keys()))))
        existing = set(chain(*query.all()))
        result = {}
        oks = releases['ok']
        records = []
        for release_id in oks.keys():
            if release_id in existing:
                result[release_id] = {
                    'status': 'error',
                    'description': "{} already exists".format(release_id)
                }
            else:
                release_raw = oks.get(release_id)

                try:
                    release = Release(
                        release_id=release_raw['id'],
                        ocid=release_raw['ocid'],
                        date=release_raw.get('date'),
                        value=release_raw
                    )
                    result[release_id] = {
                        "status": "ok",
                        "description": 'ok'
                    }
                    record = (session
                                .query(Record)
                                .filter(Record.ocid == release.ocid)
                                .first())
                    if not record:
                        record = Record(
                            ocid=release.ocid,
                            releases=[release],
                            date=release.date,
                            compiled_release=ocdsmerge.merge(
                                [release.value])
                        )
                        logger.info(f"Created record {release.ocid} with release {release.release_id}")
                    else:
                        record.releases.append(release)
                        max_date_release = max(
                            record.releases, key=operator.attrgetter('date')
                        )
                        record.date = max_date_release.date
                        record.compiled_release = ocdsmerge.merge(
                            [r.value for r in record.releases]
                        )
                        logger.info(f"Update record {release.ocid} with release {release.release_id}")
                    session.add(record)
                    records.append(record)
                    logger.info(f"Added release {release.release_id} to record {release.ocid}")

                except exc.SQLAlchemyError as e:
                    result[release_id] = {
                        'status': 'error',
                        'description': repr(e)
                    }
        result.update(releases['error'])
        self.request.registry.notify(RecordBatchUpdate(self.request, records))
        return result

    @view(renderer='simplejson', permission='view')
    def get(self):
        """ Returns list of releases in package sorted by date in descending order. """
        page_number_requested = self.request.params.get('page') or 1
        ids_only = self.request.params.get('idsOnly', '')\
                   and self.request.params.get('idsOnly').lower() in YES
        if ids_only:
            keys = (Release.release_id, Release.date, Release.ocid)
        else:
            keys = (Release.release_id, Release.date, Release.value)
        pager = SqlalchemyOrmPage(
            self.request.dbsession.query(*keys).order_by(Release.date.desc()),
            page=int(page_number_requested),
            items_per_page=self.page_size
            )

        return self.request.release_package(pager, ids_only)


@resource(
    name='release.json',
    path='/release.json',
    description="An OSDS release object can be returned. Sometimes, a user’s release ID for an API may be duplicated by chance. In such instance the user has to know either a package URL or OC ID and therefore obtain an individual release ID. It is mandatory for each release to comprise such information as an OC ID, a unique release ID, a release tag and any other characteristics of the event to be provided to the users",
    factory=factory
)
class ReleaseResource:

    def __init__(self, request, context=None):
        self.request = request

    @view(validators=(validate_release_id), renderer='simplejson', permission='view')
    def get(self):
        """ Returns a single OCDS release in format of package. """
        id_ = self.request.validated['release_id']
        release = self.request.dbsession.query(Release).filter(Release.release_id==id_).first()
        if not release:
            self.request.response.status = 404
            self.request.errors.add(
                "querystring", 'releaseID', f"Release '{id_}' Not Found"
                )
            return
        return wrap_in_release_package(
            self.request,
            [release.value],
            release.date
        )
