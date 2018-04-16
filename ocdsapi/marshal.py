from flask_restful import fields

publisher = {
    'name': fields.String(attribute='name'),
}

links_full = {
    'prev': fields.String(attribute='prev'),
    'next': fields.String(attribute='next')
}
links_partial = {
    'next': fields.String(attribute='next')
}

releases_json = {
    'publisher': fields.Nested(publisher),
    'releases': fields.Raw,
    'uri': fields.Url,
    'publishedDate': fields.String(attribute='publishedDate'),
    'license': fields.String(attribute='license'),
    'publicationPolicy': fields.String(),
}


def releases(data):
    if data.get('links', {}).get('prev'):
        return {
            'publisher': fields.Nested(publisher),
            'releases': fields.Raw,
            'uri': fields.String,
            'publishedDate': fields.String(attribute='publishedDate'),
            'license': fields.String(attribute='license'),
            'publicationPolicy': fields.String(),
            'links': fields.Nested(links_full)
        }
    else:
        return {
            'publisher': fields.Nested(publisher),
            'releases': fields.Raw,
            'uri': fields.Url,
            'publishedDate': fields.String(attribute='publishedDate'),
            'license': fields.String(attribute='license'),
            'publicationPolicy': fields.String(),
            'links': fields.Nested(links_partial)
        }
        

