#from flask import Flask, request
from flask_restful import Resource, Api
from .app import app

api = Api(app)


class ReleasesResource(Resource):

    def get(self):
        return []

class ReleaseResource(Resource):

    def get(self, release_id):
        return []


api.add_resource(ReleasesResource, '/releases.json')
api.add_resource(ReleasesResource, '/release.json/<string:release_id')
