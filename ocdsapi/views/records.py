import operator
from cornice.resource import resource, view
from sqlalchemy.orm import joinedload

from ocdsapi.models import Record
from ocdsapi.pager import Pager
from ocdsapi.validation import validate_ocid
from ocdsapi.constants import YES
from ocdsapi.utils import prepare_record,\
    wrap_in_record_package, find_max_date, factory


@resource(
    name='records.json',
    path='/records.json',
    description="This returns an object with a list of OCDS records and a links object. The records embrace all the information related to the contracting process and provide a snapshot view of its current state. These records also include a versioned history of changes that were made step by step. Only one record is possible for each contracting process, created when the releases are merged. ‘Next’ property pertaining to links object should contain the URL of the next page to be visited when scanning the results. The ‘records’ list usually contains a complete OCDS record. The search results are to be listed by modification date in descending order.",
    factory=factory
)
class RecordsResource:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context
        self.page_size = int(request.params.get('size')) \
            if (request.params.get('size')
                and str.isdigit(request.params.get('size'))) \
            else request.registry.page_size

    @view(renderer='simplejson', permission='view')
    def get(self):
        """ Returns list of records in package sorted by date in descending order. """
        ids_only = self.request.params.get('idsOnly', '')\
            and self.request.params.get('idsOnly').lower() in YES
        pager = Pager(self.request, Record, limit=self.page_size)
        return self.request.record_package(pager, ids_only)


@resource(
    name='record.json',
    path='/record.json',
    description='This is an OCDS record object supplying a snapshot of the running state of the contracting process where he information from all the preceding releases is brought together. As soon as new information is introduced, it gets updated. At least one record must be present for each contracting process in order to furnish a full list of releases associated with this contracting process.',
    factory=factory
)
class RecordResource:

    def __init__(self, request, context=None):
        self.request = request
        self.context = context

    @view(
        validators=(validate_ocid,),
        renderer='simplejson', permission='view')
    def get(self):
        """ Returns single OCDS record in package. """
        ocid = self.request.validated['ocid']
        record = (
            self.request
            .dbsession
            .query(Record)
            .filter(Record.id == ocid)
            .options(joinedload("releases").load_only("date", "ocid"))
            .first()
        )
        if not record:
            self.request.response.status = 404
            self.request.errors.add(
                "querystring", 'ocid',
                'Record {} not found'.format(ocid)
                )
            return
        date = find_max_date(record.releases)
        releases = [
            {"id": r.id, "date": r.date, "ocid": r.ocid}
            for r in record.releases
        ]
        record = prepare_record(
            self.request,
            record,
            releases,
            self.request.registry.merge_rules
            )

        return wrap_in_record_package(
            request=self.request,
            records=[record],
            date=date
        )
