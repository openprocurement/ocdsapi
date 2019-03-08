from gevent import monkey
monkey.patch_all()
import fastjsonschema
import simplejson
from logging import getLogger
from pyramid.renderers import JSON
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.config import Configurator, ConfigurationError
from ocdsmerge.merge import get_merge_rules
from ocdsapi.constants import SWAGGER, RECORD
from ocdsapi.utils import format_release_package,\
    read_datafile, format_record_package, check_credentials, BASE


logger = getLogger('ocdsapi')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.route_prefix = 'api'
        config.include('cornice')
        config.include('cornice_swagger')
        swagger_data = SWAGGER
        if settings.get('api.swagger'):
            swagger_data.update(read_datafile(settings.get('api.swagger')))
        config.registry.settings['api_specs'] = swagger_data
        config.add_route('cornice_swagger.open_api_path', '/swagger.json')
        config.add_route('health', '/health')
        config.add_route('self.schema', '/release-schema.json')
        config.cornice_enable_openapi_explorer(api_explorer_path='/swagger.ui')
        config.include('.models')
        config.add_renderer('simplejson', JSON(serializer=simplejson.dumps))
        config.add_request_method(format_release_package, name='release_package')
        config.add_request_method(format_record_package, name='record_package')
        config.registry.page_size = int(settings.get('api.page_size', 100))
        config.registry.publisher = read_datafile(settings.get('api.publisher'))
        config.registry.schema = read_datafile(settings.get('api.schema'))
        config.registry.merge_rules = get_merge_rules(settings.get('api.schema'))
        BASE['extensions'] = settings.get('api.extensions', '').split()
        config.registry.models = {
            'Release': config.registry.schema,
            'Record': RECORD
        }
        config.set_authorization_policy(ACLAuthorizationPolicy())
        tokens = [t.strip() for t in settings.get('api.tokens', '').split(',')]
        if tokens:
            config.registry.tokens = frozenset(tokens)
        config.set_authentication_policy(BasicAuthAuthenticationPolicy(check_credentials))
        config.registry.validator = None
        if settings.get('api.force_validation', False):
            config.registry.validator = fastjsonschema.compile(config.registry.schema)
        apps = settings.get('apps', '').split(',')
        for pname in apps:
            if not pname:
                continue
            try:
                app = getattr(config.maybe_dotted(pname), 'includeme', '')
                if app:
                    app(config)
                    logger.info(f"Installed app {pname}")
            except KeyError as e:
                logger.error(f"Unable to load {pname} plugin. Error: {repr(e)}")
        config.scan()
    return config.make_wsgi_app()
