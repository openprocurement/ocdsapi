import cornice
import cornice_swagger
from pyramid.view import view_config
from ocdsapi.constants import DESCRIPTIONS, RESPONSES, RECORD
from deep_merge import merge


@view_config(
    renderer='simplejson',
    route_name='cornice_swagger.open_api_path',
    request_method='GET'
)
def swagger_json(request):
    services = cornice.service.get_services()
    swagger = cornice_swagger.CorniceSwagger(
        services,
        pyramid_registry=request.registry
    )
    swagger.base_path = '/api'
    swagger.summary_docstrings = True
    info = request.registry.settings['api_specs']
    base = swagger.generate(**info, info=info)
    for path in base['paths'].keys():
        for doc in (DESCRIPTIONS, RESPONSES):
            merge(base['paths'][path], doc[path.lstrip('/')])

    base['models'] = request.registry.models
    # This is private endpoint
    del(base['paths']['/releases.json']['post'])
    return base
