import cornice
import cornice_swagger
from pyramid.view import view_config
from ocdsapi.constants import DESCRIPTIONS, RESPONSES


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
    swagger.summary_docstrings = True
    info = request.registry.settings['api_specs']
    base = swagger.generate(**info, info=info)
    for path in base['paths'].keys():
        for doc in (DESCRIPTIONS, RESPONSES):
            base['paths'][path].update(
                doc[path.lstrip('/')]
            )
    base['definitions'] = {}
    base['definitions']['Release'] = request.registry.schema
    return base