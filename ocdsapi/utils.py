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
        'releases': releases,
        'compiledRelease': ocdsmerge.merge(
            releases, merge_rules=merge_rules
        ),
        'versionedRelease': ocdsmerge.merge_versioned(
            releases, merge_rules=merge_rules
        ),
        'ocid': ocid,
    }
    return record


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
    return {
        **BASE,
        **request.registry.publisher,
        'releases': releases,
        'publishedDate': date,
        'uri': request.current_route_url(),
        'links': links
    }


def format_record_package(request, pager):
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

    date = max(dates)
    next_page = pager.next_page if pager.next_page else pager.page,
    links = {
        'total': pager.page_count,
        'next': request.route_url('records.json', _query=(('page', next_page),))
    }
    if pager.previous_page:
        links['prev'] = request.route_url(
            'records.json', _query=(('page', pager.previous_page),)
        )
    return {
        **BASE,
        **request.registry.publisher,
        'records': records,
        'publishedDate': date,
        'uri': request.current_route_url(),
        'links': links
    }