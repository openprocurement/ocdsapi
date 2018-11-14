from pyramid.view import view_config


@view_config(renderer='simplejson', route_name='health')
def health(request):
    return {
        "staus": "ok"
    }