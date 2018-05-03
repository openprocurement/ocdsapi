import argparse
# import ocdsmerge

# TODO: ocdsmerge seems to be broken. check how to make it work
# def compile_releases(releases, versioned=False):
#     return ocdsmerge.merge(releases) if not versioned\
#         else ocdsmerge.merge_versioned(releases)


# def form_record(releases):
#     record = {}
#     record['releases'] = [releases]
#     record['compiledRelease'] = compile_releases(record['releases'])
#     record['ocid'] = record['releases'][0]['ocid']
#     return record


def prepare_responce_doc(doc):
    doc.pop('_rev')
    doc['id'] = doc.pop('_id')
    return doc


def build_meta(options):
    return {
        'publisher': {
            'name': options.get('publisher.name', ''),
        },
        'license': options.get('license', ''),
        'publicationPolicy': options.get('publicationPolicy', '')
    }


def get_or_create_db(server, name):
    if name not in server:
        server.create(name)
    return server[name]