import fastjsonschema
import simplejson
from logging import getLogger
from pyramid.renderers import JSON
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.config import Configurator, ConfigurationError
from zope.dottedname import resolve
from elasticsearch import Elasticsearch
from ocdsmerge.merge import process_schema
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
        config.registry.global_config = global_config
        swagger_data = SWAGGER
        if settings.get('api.swagger'):
            swagger_data.update(read_datafile(settings.get('api.swagger')))
        elasticsearch = settings.get("elasticsearch.url")
        config.registry.es = None
        if elasticsearch:
            es = Elasticsearch([elasticsearch])
            index = settings.get("elasticsearch.index", 'releases')
            config.registry.es = es
            config.registry.es_index = index
            es.indices.create(index=index, ignore=400)
            logger.info(f"Created index {index}")
            mapping_ = settings.get("elasticsearch.mapping")
            if mapping_:
                with open(mapping_) as _in:
                    mapping = simplejson.load(_in)
                    es.indices.put_mapping(
                        doc_type='Tender',
                        index=index,
                        body=mapping
                    )
                    logger.info(f"Updated mapping for elasticsearch {mapping_}")
        config.registry.settings['api_specs'] = swagger_data
        config.add_route('cornice_swagger.open_api_path', '/swagger.json')
        config.add_route('health', '/health')
        config.cornice_enable_openapi_explorer(api_explorer_path='/swagger.ui')
        config.include('.models')
        config.add_renderer('simplejson', JSON(serializer=simplejson.dumps))
        config.add_request_method(format_release_package, name='release_package')
        config.add_request_method(format_record_package, name='record_package')
        config.registry.page_size = int(settings.get('api.page_size', 100))
        config.registry.publisher = read_datafile(settings.get('api.publisher'))
        config.registry.schema = read_datafile(settings.get('api.schema'))
        config.registry.merge_rules = process_schema(settings.get('api.schema'))
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
        for app in apps:
            if not app:
                continue
            path, _, plugin = app.partition(':')
            if not plugin:
                plugin = 'includeme'
            try:
                module = resolve.resolve(path)
                if hasattr(module, plugin):
                    getattr(module, plugin)(config)
                else:
                    logger.error(f"App {path} unavailable, check your configuration")
            except KeyError as e:
                logger.error(f"Unable to load {path} plugin. Error: {repr(e)}")
        config.scan()
    return config.make_wsgi_app()
