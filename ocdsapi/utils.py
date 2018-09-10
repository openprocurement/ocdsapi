from datetime import datetime
from json import load
from os import path
import operator
import yaml
import ocdsmerge


DEFAULT_EXTENSIONS = [
    "https://raw.githubusercontent.com/open-contracting/api_extension/eeb2cb400c6f1d1352130bd65b314ab00a96d6ad/extension.json"
]
THIS = path.dirname(path.abspath(__file__))


def prepare_record(releases):
    if not releases:
        return {}
    # import pdb; pdb.set_trace()
    ocids = {rel['ocid'] for rel in releases}
    if len(ocids) > 1:
        raise ValueError("Different ocids in same record {}".format(
            ocids
        ))
    record = {
        'releases': releases,
        'compiledRelease': ocdsmerge.merge(releases),
        'versionedRelease': ocdsmerge.merge_versioned(releases),
        'ocid': ocids.pop(),
    }
    return record


def prepare_responce_doc(doc):
    doc.pop('_rev', '')
    doc.pop('$schema', '')
    if doc.get('_id'):
        doc['id'] = doc.pop('_id')
    return doc


def ids_only(doc):
    return {
        "id": doc.pop('id'),
        "ocid": doc.pop('ocid')
    }


def build_meta(options):
    """
    Prepare package metadata(license, publicationPolicy ...)
    """
    base = {
        'publisher': {
            'name': None,
            'scheme': None,
            'uri': None
        },
        'license': None,
        'publicationPolicy': None,
        'version': options.get('version', "1.1"),
        'extensions': DEFAULT_EXTENSIONS
    }

    if 'metainfo.file' in options:
        info = options['metainfo.file']
        with open(info) as _in:
            metainfo = yaml.load(_in)
        base.update(metainfo)
        return base
    else:
        return {
            'publisher': {
                'name': options.get('publisher.name'),
                'scheme': options.get('publisher.scheme'),
                'uri': options.get('publisher.uri')
            },
            'license': options.get('license'),
            'publicationPolicy': options.get('publicationPolicy'),
            'version': options.get('version', "1.1")
        }


def get_or_create_db(server, name):
    """
    Return existing db instance or create new one
    """
    if name not in server:
        server.create(name)
    return server[name]


def find_max_date(items):
    if not items:
        return datetime.now().isoformat()
    return max(items, key=operator.itemgetter('date')).get('date')


def read_datafile(name):
    with open(path.join(THIS, 'doc', name)) as fd:
        return load(fd)
