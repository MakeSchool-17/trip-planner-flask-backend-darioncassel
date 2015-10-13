from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
import bcrypt

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)


# Implement REST Resource
class Register(Resource):

    def post(self):
        user_collection = app.db.users
        pw_bytes = request.json["password"].encode('utf-8')
        hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(12))
        user = {
            "username": request.json["username"],
            "password": hashed.decode('utf-8')
        }
        result = user_collection.insert_one(user)
        user = user_collection.find_one(
            {"_id": ObjectId(result.inserted_id)})
        return user


# Implement REST Resource
class Login(Resource):

    def post(self):
        user_collection = app.db.users
        result = user_collection.find_one(
            {"username": request.json["username"]})
        if result:
            pw_bytes = request.json["password"].encode('utf-8')
            h_bytes = result["password"].encode('utf-8')
            if bcrypt.hashpw(pw_bytes, h_bytes) == h_bytes:
                response = jsonify({"username": result["username"]})
                response.status_code = 200
                return response
            else:
                response = jsonify(data=[])
                response.status_code = 401
                return response
        else:
            response = jsonify(data=[])
            response.status_code = 401
            return response


# Implement REST Resource
class Trip(Resource):

    def post(self):
        trip_collection = app.db.trips
        result = trip_collection.insert_one(request.json)
        trip = trip_collection.find_one(
            {"_id": ObjectId(result.inserted_id)})
        return trip

    def get(self, trip_id=None):
        trip_collection = app.db.trips
        if not trip_id:
            cursors = trip_collection.find()
            trips = []
            for trip in cursors:
                trips.append(trip)
            return trips
        else:
            trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
            if trip is None:
                response = jsonify(data=[])
                response.status_code = 404
                return response
            else:
                return trip

    def put(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            result = trip_collection.replace_one({"_id": ObjectId(trip_id)},
                                                 request.json)
            if result.modified_count == 1:
                trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
                return trip
            else:
                response = jsonify(data=[])
                response.status_code = 500
                return response

    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            result = trip_collection.delete_one({"_id": ObjectId(trip_id)})
            if result.deleted_count == 1:
                response = jsonify(data=[])
                response.status_code = 200
                return response
            else:
                response = jsonify(data=[])
                response.status_code = 500
                return response


# Add REST resources to API
api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>')
api.add_resource(Register, '/register/')
api.add_resource(Login, '/login/')


# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about
    # request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
