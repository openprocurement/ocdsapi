import operator
import ocdsmerge
import json
import yaml
from datetime import datetime
from collections import defaultdict


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
    return max(items, key=operator.itemgetter('date')).get('date')


def prepare_record(ocid, releases, merge_rules):
    if not releases:
        return {}

    record = {
        'releases': sorted(releases, key=operator.itemgetter('date')),
        'compiledRelease': ocdsmerge.merge(
            releases, merge_rules=merge_rules
        ),
        'versionedRelease': ocdsmerge.merge_versioned(
            releases, merge_rules=merge_rules
        ),
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
    if ids_only:
        releases = [
            {"id": item[0], "ocid": item[1]}
            for item in pager.items
        ]
        date = max((item[2] for item in pager.items)).isoformat()
    else:
        releases = [item.value for item in pager.items]
        date = find_max_date(releases)
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
    grouped = defaultdict(list)
    for release in pager.items:
        grouped[release.ocid].append(release.value)
    records = []
    dates = []
    for ocid, releases in grouped.items():
        dates.append(find_max_date(releases))
        records.append(
            prepare_record(
                ocid,
                releases,
                request.registry.merge_rules
            )
        )
    date = max(dates) if dates else datetime.now().isoformat()
    next_page = pager.next_page if pager.next_page else pager.page,
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

    linked_releases = [
        {
            "url": request.route_url('release.json', _query=(('releaseID', item.release_id),)),
            "date": item.date.isoformat()
        }
        for item in pager.items
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