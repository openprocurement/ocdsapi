import fastjsonschema
from pyramid.config import Configurator, ConfigurationError
from ocdsmerge.merge import process_schema
from ocdsapi.utils import format_release_package,\
    read_datafile, format_record_package


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('cornice')
        config.include('cornice_swagger')
        config.include('pyramid_celery')
        config.include('.models')
        config.add_request_method(format_release_package, name='release_package')
        config.add_request_method(format_record_package, name='record_package')
        config.registry.page_size = int(settings.get('api.page_size', 100))
        config.registry.publisher = read_datafile(settings.get('api.publisher'))
        config.registry.schema = read_datafile(settings.get('api.schema'))
        config.registry.merge_rules = process_schema(settings.get('api.schema'))
        config.registry.validator = fastjsonschema.compile(config.registry.schema)
        config.scan()
    return config.make_wsgi_app()