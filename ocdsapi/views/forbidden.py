from pyramid.view import forbidden_view_config, notfound_view_config


@forbidden_view_config(renderer='simplejson')
def forbidden(request):
    return {'status': 'error', "description": "Forbidden"}


@notfound_view_config(renderer='simplejson')
def not_found(request):
    request.response.status = 404
    return {"status": "Not Found"}