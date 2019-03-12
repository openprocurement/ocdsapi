import operator
import ocdsmerge
import json
import yaml
from datetime import datetime
from pyramid.security import (
    Allow,
    Everyone,
)
from ocdsapi.models import get_session_factory, get_engine, Record

BASE = {
    'publisher': {
        'name': None,
        'scheme': None,
        'uri': None
    },
    'license': None,
    'publicationPolicy': None,
    'version': "1.1",
    'extensions': []
}


def read_datafile(path):
    loader = json.load if path.endswith('json')\
        else yaml.load
    with open(path) as fd:
        return loader(fd)


def find_max_date(items):
    if not items:
        return datetime.now().isoformat()
    return max(items, key=operator.attrgetter('date')).date


def prepare_record(request, record, releases, merge_rules):
    if not releases:
        return {}
    try:
        compiledRelease = record.compiled_release
    except Exception:
        compiledRelease = ocdsmerge.merge(
                releases, merge_rules=request.registry.merge_rules
            )
    record = {
        'releases': [
            linked_release(request, release)
            for release in sorted(
                releases, key=operator.itemgetter('date')
                )
        ],
        'compiledRelease': compiledRelease,
        # TODO: fix after optimization
        # 'versionedRelease': ocdsmerge.merge_versioned(
        #     releases, merge_rules=merge_rules
        # ),
        'ocid': record.id,
    }
    return record


def wrap_in_release_package(request, releases, date):
    return {
        **BASE,
        **request.registry.publisher,
        'releases': releases,
        'publishedDate': date,
        'uri': request.current_route_url(),
    }


def get_ids_only(row):
    return {"id": row.id, "ocid": row.ocid}


def release_package(request, pager, ids_only=False):
    items, next_token, prev_token = pager.run()
    max_date = max([release.date for release in items]) if items \
        else datetime.now().isoformat()
    getter = operator.attrgetter('value') if not ids_only else get_ids_only
    releases = [getter(row) for row in items]
    package = wrap_in_release_package(request, releases, max_date)
    package['links'] = {
        'next': request.route_url(
            'releases.json',
            _query=(('page', next_token), ('size', pager.limit))
            if pager.limit != request.registry.page_size
            else (('page', next_token),)),
        'prev': request.route_url(
            'releases.json',
            query=(('page', prev_token), ('size', pager.limit))
            if pager.limit != request.registry.page_size
            else (('page', prev_token),)),
        }

    return package


def linked_release(request, release):
    return {
        'url': request.route_url(
            'release.json', _query=(('releaseID', release['id']),)
            ),
        'date': release['date']
    }


def record_package(request, pager, ids_only=False):

    items, next_token, prev_token = pager.run()

    records = [prepare_record(request, record,
                              [{"id": r.id, "date": r.date, "ocid": r.id}
                               for r in record.releases],
                              request.registry.merge_rules)
               if not ids_only else
               {"id": record.compiled_release['id'], "ocid": record.id}
               for record in items]

    max_date = max([find_max_date(record.releases) for record in items]) \
        if items else datetime.now().isoformat()

    links = {
        'next': request.route_url(
            'records.json',
            _query=(('page', next_token), ('size', pager.limit))
            if pager.limit != request.registry.page_size
            else (('page', next_token),)),
        'prev': request.route_url(
            'records.json',
            query=(('page', prev_token), ('size', pager.limit))
            if pager.limit != request.registry.page_size
            else (('page', prev_token),)),
        }

    return wrap_in_record_package(
        request=request,
        records=records,
        date=max_date,
        links=links
    )


def wrap_in_record_package(*, request,
                           date, records, links={}):
    return {
        **BASE,
        **request.registry.publisher,
        'records': records,
        'publishedDate': date,
        'uri': request.current_route_url(),
        'links': links
    }


def check_credentials(username, password, request):
    tokens = request.registry.tokens
    if (username in tokens) or (password in tokens):
        return ['worker']


class Root:
    __acl__ = [
        (Allow, 'worker', 'create'),
        (Allow, Everyone, 'view')
    ]


def factory(request):
    return Root()


def get_db_session(settings):
    factory = get_session_factory(get_engine(settings))
    return factory()

