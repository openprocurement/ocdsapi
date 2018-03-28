from flask import Flask, jsonify, request, abort
from openprocurement.ocds.api.storage import ReleaseStorage
from openprocurement.ocds.api.utils import (
    parse_args,
    read_config,
    form_next_date,
    get_releases_list,
    get_package_url,
    form_record,
    get_records_list
)
app = Flask(__name__)
REGISTRY = {
    "config": None,
    "storage": None,
}


def create_app():

    @app.route("/release.json")
    def release():
        id = request.args.get('id', None)
        ocid = request.args.get('ocid', None)
        package_url = request.args.get('packageURL', None)
        if id:
            if id in REGISTRY['storage'].db:
                if package_url:
                    return jsonify({"package_url": get_package_url(REGISTRY['storage'],
                                                                   request,
                                                                   id=id)})
                return jsonify(REGISTRY['storage'].get_by_id(id))
            else:
                abort(404)
        elif ocid:
            if REGISTRY['storage'].get_by_ocid(ocid):
                if package_url:
                    return jsonify({"package_url": get_package_url(REGISTRY['storage'],
                                                                   request,
                                                                   ocid=ocid)})
                return jsonify(REGISTRY['storage'].get_by_ocid(ocid))
            else:
                abort(404)
        else:
            return jsonify({"error": "ReleaseID is required"})

    @app.route("/releases.json")
    def releases():
        link = '{}?start_date={}&end_date={}'
        base_url = request.url.split('?')[0]
        global_start_date, global_end_date = REGISTRY['storage'].get_dates()
        if request.args.get('page'):
            next_page_dates = form_next_date(
                global_start_date, request.args.get('page'))
            if global_end_date < next_page_dates[2]:
                return jsonify({"error": "Page does not exist"})
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "releases": get_releases_list(request,
                                                  next_page_dates[2],
                                                  next_page_dates[0],
                                                  REGISTRY['storage'])
                }
            })
        elif not request.args.get('start_date') and not request.args.get('end_date'):
            next_page_dates = form_next_date(global_start_date, page=1)
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "releases": get_releases_list(request,
                                                  next_page_dates[2],
                                                  next_page_dates[0],
                                                  REGISTRY['storage'])
                }
            })
        elif request.args.get('start_date') and request.args.get('end_date'):
            next_page_dates = form_next_date(request.args.get('end_date'))
            if global_end_date < request.args.get('start_date'):
                return jsonify({"error": "You have reached maximum date"})
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "releases": get_releases_list(request,
                                                  request.args.get(
                                                      'start_date'),
                                                  next_page_dates[0],
                                                  REGISTRY['storage'])
                }
            })

    @app.route("/record.json")
    def record():
        ocid = request.args.get("ocid", None)
        if ocid:
            return jsonify(form_record(REGISTRY['storage'].get_by_ocid(ocid)))
        else:
            return jsonify({"error": "You must provide OCID"})

    @app.route("/records.json")
    def records():
        link = '{}?start_date={}&end_date={}'
        base_url = request.url.split('?')[0]
        global_start_date, global_end_date = REGISTRY['storage'].get_dates()
        if request.args.get('page'):
            next_page_dates = form_next_date(
                global_start_date, request.args.get('page'))
            if global_end_date < next_page_dates[2]:
                return jsonify({"error": "Page does not exist"})
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "records": get_records_list(request,
                                                next_page_dates[2],
                                                next_page_dates[0],
                                                REGISTRY['storage'])
                }
            })
        elif not request.args.get('start_date') and not request.args.get('end_date'):
            next_page_dates = form_next_date(global_start_date, page=1)
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "records": get_records_list(request,
                                                next_page_dates[2],
                                                next_page_dates[0],
                                                REGISTRY['storage'])
                }
            })
        elif request.args.get('start_date') and request.args.get('end_date'):
            next_page_dates = form_next_date(request.args.get('end_date'))
            if global_end_date < request.args.get('start_date'):
                return jsonify({"error": "You have reached maximum date"})
            return jsonify({
                "links": {
                    "next": link.format(base_url,
                                        next_page_dates[0],
                                        next_page_dates[1]),
                    "records": get_records_list(request,
                                                request.args.get(
                                                    'start_date'),
                                                next_page_dates[0],
                                                REGISTRY['storage'])
                }
            })
    return app


def run(config, **kwargs):
    REGISTRY['storage'] = ReleaseStorage(kwargs.get("couch_host"),
                                         kwargs.get("couch_port"),
                                         kwargs.get("releases_db"))
    app = create_app()
    return app
