from pyramid.view import forbidden_view_config


@forbidden_view_config(renderer='simplejson')
def forbidden(request):
    return {'status': 'error', "description": "Forbidden"}