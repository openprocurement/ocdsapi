from flask import Flask, jsonify, request
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
    "app": Flask(__name__),
    "db": None,
}


@app.route("/release.json")
def release():
    id = request.args.get('id', None)
    ocid = request.args.get('ocid', None)
    package_url = request.args.get('packageURL', None)
    if id:
        if package_url:
            return {"package_url": get_package_url(REGISTRY['db'], request, id=id)}
        return jsonify(REGISTRY['db'].get_by_id(id))
    elif ocid:
        if package_url:
            return {"package_url": get_package_url(REGISTRY['db'], request, ocid=ocid)}
        return jsonify(REGISTRY['db'].get_by_ocid(ocid))
    else:
        return "ReleaseID is required"


@app.route("/releases.json")
def releases():
    link = '{}?start_date={}&end_date={}'
    base_url = request.url.split('?')[0]
    start_date, end_date = REGISTRY['db'].get_dates()
    if request.args.get('page'):
        next_page_dates = form_next_date(start_date, request.args.get('page'))
        if end_date < next_page_dates[1]:
            return "You have reached maximum date"
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_releases_list(request,
                                              next_page_dates[2],
                                              next_page_dates[0],
                                              REGISTRY['db'])
            }
        })
    elif not request.args.get('start_date') and not request.args.get('end_date'):
        next_page_dates = form_next_date(start_date, page=1)
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_releases_list(request,
                                              next_page_dates[2],
                                              next_page_dates[0],
                                              REGISTRY['db'])
            }
        })
    elif request.args.get('start_date') and request.args.get('end_date'):
        next_page_dates = form_next_date(request.args.get('end_date'))
        if end_date < next_page_dates[1]:
            return "You have reached maximum date"
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_releases_list(request,
                                              request.args.get('start_date'),
                                              next_page_dates[0],
                                              REGISTRY['db'])
            }
        })


@app.route("/record.json")
def record():
    ocid = request.args.get("ocid", None)
    if ocid:
        return jsonify(form_record(REGISTRY['db'].get_by_ocid(ocid)))
    else:
        return "You must provide OCID"


@app.route("/records.json")
def records():
    link = '{}?start_date={}&end_date={}'
    base_url = request.url.split('?')[0]
    start_date, end_date = REGISTRY['db'].get_dates()
    if request.args.get('page'):
        next_page_dates = form_next_date(start_date, request.args.get('page'))
        if end_date < next_page_dates[1]:
            return "You have reached maximum date"
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_records_list(request,
                                             next_page_dates[2],
                                             next_page_dates[0],
                                             REGISTRY['db'])
            }
        })
    elif not request.args.get('start_date') and not request.args.get('end_date'):
        next_page_dates = form_next_date(start_date, page=1)
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_records_list(request,
                                             next_page_dates[2],
                                             next_page_dates[0],
                                             REGISTRY['db'])
            }
        })
    elif request.args.get('start_date') and request.args.get('end_date'):
        next_page_dates = form_next_date(request.args.get('end_date'))
        if end_date < next_page_dates[1]:
            return "You have reached maximum date"
        return jsonify({
            "links": {
                "next": link.format(base_url,
                                    next_page_dates[0],
                                    next_page_dates[1]),
                "releases": get_records_list(request,
                                             request.args.get('start_date'),
                                             next_page_dates[0],
                                             REGISTRY['db'])
            }
        })


def run():
    args = parse_args()
    config = read_config(args.config)
    REGISTRY['db'] = ReleaseStorage(config.get('db'))
    app.run()
