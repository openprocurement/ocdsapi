import yaml
import ocdsmerge

DEFAULT_EXTENSIONS = [
    "https://raw.githubusercontent.com/open-contracting/api_extension/eeb2cb400c6f1d1352130bd65b314ab00a96d6ad/extension.json"
]


def prepare_record(releases, ocid):
    if not isinstance(releases, list):
        releases = [releases]
    record = {
        'releases': releases,
        'compiledRelease': ocdsmerge.merge(releases),
        'versionedRelease': ocdsmerge.merge_versioned(releases),
        'ocid': ocid,
    }
    return record


def prepare_responce_doc(doc):
    doc.pop('_rev')
    doc.pop('$schema')
    doc['id'] = doc.pop('_id')
    return doc


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
