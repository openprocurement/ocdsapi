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
        'ocid': record.ocid,
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


def format_release_package(request, pager, ids_only=False):
    dates = [item[1] for item in pager.items]
    date = max(dates)\
        if dates else datetime.now().isoformat()
    if ids_only:
        releases = [
            {"id": item[0], "ocid": item[2]}
            for item in pager.items
        ]

    else:
        releases = [
            item[2] for item in pager.items
        ]

    next_page = pager.next_page if pager.next_page else pager.page,
    links = {
        # 'total': pager.page_count,
        'next': request.route_url(
            'releases.json', _query=(('page', next_page),)
            )
    }
    if pager.previous_page:
        links['prev'] = request.route_url(
            'releases.json', _query=(('page', pager.previous_page),)
        )
    package = wrap_in_release_package(request, releases, date)
    package['links'] = links
    return package


def linked_release(request, release):
    return {
        'url': request.route_url(
            'release.json', _query=(('releaseID', release['id']),)
            ),
        'date': release['date']
    }


def format_record_package(request, pager, ids_only=False):

    records = []
    dates = []

    for record in pager.items:
        dates.append(find_max_date(record.releases))
        records.append(
            prepare_record(
                request,
                record,
                [{
                    "id": r.release_id,
                    "date": r.date,
                    "ocid": r.ocid
                } for r in record.releases],
                request.registry.merge_rules
            )
        )
    date = max(dates) if dates else datetime.now().isoformat()
    next_page = pager.next_page if pager.next_page else 1
    links = {
        # 'total': pager.page_count,
        'next': request.route_url(
            'records.json', _query=(('page', next_page),)
            )
    }
    if pager.previous_page:
        links['prev'] = request.route_url(
            'records.json', _query=(('page', pager.previous_page),)
        )
    if ids_only:
        records = [
            {"id": r['compiledRelease']['id'], "ocid": r['ocid']}
            for r in records
        ]

    return wrap_in_record_package(
        request=request,
        records=records,
        date=date,
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

