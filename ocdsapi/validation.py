import hashlib
from fastjsonschema import JsonSchemaException


def validate_release_bulk(request, **kw):
    data = request.json_body
    releases = data.get('releases')
    if not releases:
        request.errors.add('data', 'releases', 'releases data missing')
    validator = request.registry.validator
    request.validated['releases'] = {}
    for release in releases:
        try:
            release_id = hashlib.md5(str(release).encode('utf-8')).hexdigest()
            release['id'] = release_id
            request.validated['releases'][release_id] = validator(release)
        except JsonSchemaException as e:
            request.errors.add("data", "release", e.message)


def validate_ocid(request, **kw):
    ocid = request.params.get('ocid')
    if not ocid:
        request.errors.add("querystring", 'ocid', 'ocid query argument missing')
    request.validated['ocid'] = ocid

def validate_release_id(request, **kw):
    id_ = request.params.get('releaseID')
    if not id_:
        request.errors.add("querystring", 'releaseID', 'releaseID required')
        return
    request.validated['release_id'] = id_