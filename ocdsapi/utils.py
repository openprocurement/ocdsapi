import yaml
import ocdsmerge


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
    base = {
        'publisher': {
            'name': '',
            'scheme': '',
            'uri': ''
        },
        'license': '',
        'publicationPolicy': '',
        'version': options.get('version', "1.1")
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
                'name': options.get('publisher.name', ''),
                'scheme': options.get('publisher.scheme', ''),
                'uri': options.get('publisher.uri', '')
            },
            'license': options.get('license', ''),
            'publicationPolicy': options.get('publicationPolicy', ''),
            'version': options.get('version', "1.1")
        }


def get_or_create_db(server, name):
    if name not in server:
        server.create(name)
    return server[name]
