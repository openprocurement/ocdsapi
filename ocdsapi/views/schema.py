from pyramid.view import view_config


@view_config(
    renderer='simplejson',
    route_name='self.schema',
    request_method='GET'
)
def swagger_json(request):
    return request.registry.schema
