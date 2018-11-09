from cornice.resource import resource, view
from paginate_sqlalchemy import SqlalchemyOrmPage
from ocdsapi.models import Release
from ocdsapi.validation import validate_ocid
from ocdsapi.constants import YES
from ocdsapi.utils import prepare_record,\
    wrap_in_record_package, find_max_date

@resource(
    name='records.json',
    path='/records.json',
    description="This returns an object with a list of OCDS records and a links object. The records embrace all the information related to the contracting process and provide a snapshot view of its current state. These records also include a versioned history of changes that were made step by step. Only one record is possible for each contracting process, created when the releases are merged. ‘Next’ property pertaining to links object should contain the URL of the next page to be visited when scanning the results. The ‘records’ list usually contains a complete OCDS record. The search results are to be listed by modification date in descending order."
)
class RecordsResource:

    def __init__(self, request, context=None):
        self.request = request
        self.query = (request
                      .dbsession
                      .query(Release)
                      .order_by(Release.date.desc(), Release.ocid))
        self.page_size = request.registry.page_size

    @view(renderer='simplejson')
    def get(self):
        """ Returns list of records in package sorted by date in descending order. """
        page_number_requested = self.request.params.get('page') or 1
        ids_only = self.request.params.get('idsOnly', '')\
            and self.request.params.get('idsOnly').lower() in YES
        pager = SqlalchemyOrmPage(
            self.query,
            page=int(page_number_requested),
            items_per_page=self.page_size
        )
        return self.request.record_package(pager, ids_only)


@resource(
    name='record.json',
    path='/record.json',
    description='This is an OCDS record object supplying a snapshot of the running state of the contracting process where he information from all the preceding releases is brought together. As soon as new information is introduced, it gets updated. At least one record must be present for each contracting process in order to furnish a full list of releases associated with this contracting process.',
)
class RecordResource:

    def __init__(self, request, context=None):
        self.request = request

    @view(validators=(validate_ocid,), renderer='simplejson')
    def get(self):
        """ Returns single OCDS record in package. """
        ocid = self.request.validated['ocid']
        releases = [
            item.value
            for item in
            self.request.dbsession.query(Release).filter(Release.ocid==ocid).all()
        ]
        record = prepare_record(ocid, releases, self.request.registry.merge_rules)
        linked_releases = [{
            "url": self.request.route_url('release.json', _query=(('releaseID', r['id']),)),
            "date": r['date']
            }
            for r in releases
        ]
        return wrap_in_record_package(
            request=self.request,
            linked_releases=linked_releases,
            records=[record],
            date=find_max_date(releases)
        )