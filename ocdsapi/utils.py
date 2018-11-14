import operator
import ocdsmerge
import json
import yaml
from datetime import datetime
from pyramid.security import (
    Allow,
    Everyone,
)
from ocdsapi.models import get_session_factory, get_engine


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


def prepare_record(ocid, releases, merge_rules):
    if not releases:
        return {}

    record = {
        'releases': sorted(releases, key=operator.itemgetter('date')),
        'compiledRelease': ocdsmerge.merge(
            releases, merge_rules=merge_rules
        ),
        # TODO: fix after optimization
        # 'versionedRelease': ocdsmerge.merge_versioned(
        #     releases, merge_rules=merge_rules
        # ),
        'ocid': ocid,
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
    date = max((item[1] for item in pager.items))
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
        'total': pager.page_count,
        'next': request.route_url('releases.json', _query=(('page', next_page),))
    }
    if pager.previous_page:
        links['prev'] = request.route_url(
            'releases.json', _query=(('page', pager.previous_page),)
        )
    package = wrap_in_release_package(request, releases, date)
    package['links'] = links
    return package


def format_record_package(request, pager, ids_only=False):

    records = []
    dates = []
    linked_releases = []

    for record in pager.items:
        dates.append(find_max_date(record.releases))
        for release in record.releases:
            linked_releases.append({
                'url': request.route_url('release.json', _query=(('releaseID', release.release_id),)),
                'date': release.date
            })
        records.append(
            prepare_record(
                record.ocid,
                [r.value for r in record.releases],
                request.registry.merge_rules
            )
        )
    date = max(dates) if dates else datetime.now().isoformat()
    next_page = pager.next_page if pager.next_page else 1
    links = {
        'total': pager.page_count,
        'next': request.route_url('records.json', _query=(('page', next_page),))
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
        linked_releases=linked_releases,
        records=records,
        date=date
    )


def wrap_in_record_package(*, request, linked_releases, date, records):
    return {
        **BASE,
        **request.registry.publisher,
        'records': records,
        'publishedDate': date,
        'uri': request.current_route_url(),
        'releases': linked_releases
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