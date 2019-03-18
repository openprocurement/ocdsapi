import hashlib
from json import JSONDecodeError
from fastjsonschema import JsonSchemaException


def validate_release_bulk(request, **kw):
    try:
        data = request.json_body
        releases = data.get('releases')
        if not releases:
            request.errors.add('body', 'releases', 'releases data missing')
            return
        if not isinstance(releases, list):
            request.errors.add(
                'body', 'releases', 'releases data is not an array'
            )
            return
        validator = request.registry.validator
        request.validated['releases'] = {
            'ok': {},
            'error': {}
        }
        for release in releases:
            release.pop('id', '')  # can change
            release.pop('$schema', '')  # not used
            id = hashlib.md5(str(release).encode('utf-8')).hexdigest()
            release['id'] = id
            try:
                release = release if not validator else validator(release)
                request.validated['releases']['ok'][id] = release
            except JsonSchemaException as e:
                request.validated['releases']['error'][id] = e.message
    except JSONDecodeError as e:
        request.errors.add("body", "releases", "Invalid json content")


def validate_ocid(request, **kw):
    ocid = request.params.get('ocid')
    if not ocid:
        request.errors.add("querystring", 'ocid', 'ocid query argument missing')
        return
    request.validated['ocid'] = ocid


def validate_release_id(request, **kw):
    id_ = request.params.get('releaseID')
    if not id_:
        request.errors.add("querystring", 'releaseID', 'releaseID required')
        return
    request.validated['id'] = id_
