from cornice.resource import resource, view
from paginate_sqlalchemy import SqlalchemyOrmPage
from ocdsapi.models import Release
from ocdsapi.utils import prepare_record
from ocdsapi.validation import validate_ocid
from ocdsapi.constants import YES


@resource(
    name='records.json',
    path='/records.json',
    description=""
)
class RecordsResource:

    def __init__(self, request, context=None):
        self.request = request
        self.query = request.dbsession.query(Release).order_by(Release.ocid)
        self.page_size = request.registry.page_size

    @view(renderer='simplejson')
    def get(self):
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
    description='',
)
class RecordResource:

    def __init__(self, request, context=None):
        self.request = request

    @view(validators=(validate_ocid,), renderer='simplejson')
    def get(self):
        ocid = self.request.validated['ocid']
        releases = [
            item.value
            for item in
            self.request.dbsession.query(Release).filter(Release.ocid==ocid).all()
        ]
        return prepare_record(ocid, releases, self.request.registry.merge_rules)