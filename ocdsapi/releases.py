from flask_restful import Resource, reqparse, abort


collection_options = reqparse.RequestParser()
collection_options.add_argument("idsOnly", type=bool)
collection_options.add_argument("page", type=str)
collection_options.add_argument("packageURL", type=str)
collection_options.add_argument("releaseID", type=str)

release_options = reqparse.RequestParser()
release_options.add_argument(
    "releaseID",
    type=str,
    required=True,
    help="Provide valid releaseID"
    )
release_options.add_argument("packageURL", type=str)
release_options.add_argument("ocid", type=str)


class ReleasesResource(Resource):

    def get(self):
        return []
