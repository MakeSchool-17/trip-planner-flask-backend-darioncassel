import server
import unittest
import json
from pymongo import MongoClient


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True
        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db
        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('trips')

    # Trip tests

    def test_create_trip(self):
        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip"
                                     )),
                                 content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A Trip' in responseJSON["name"]

    def test_update_trip(self):
        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip"
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.put('/myobject/'+postedObjectID,
                                data=json.dumps(dict(
                                    name="A Trip"
                                    )),
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A Trip' in responseJSON["name"]

    def test_update_non_existent_trip(self):
        response = self.app.put('/myobject/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    def test_delete_trip(self):
        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip"
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/myobject/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A Trip' in responseJSON["name"]

    def test_delete_non_existent_trip(self):
        response = self.app.delete('/myobject/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    def test_get_trip_by_id(self):
        response = self.app.post('/myobject/',
                                 data=json.dumps(dict(
                                     name="Another object"
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/myobject/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another object' in responseJSON["name"]

    def test_get_non_existent_trip(self):
        response = self.app.get('/myobject/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    def test_get_all_trips_for_user(self):
        response = self.app.post('/myobject/',
                                 data=json.dumps(dict(
                                     name="Another object"
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]
        response = self.app.get('/myobject/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert 'Another object' in responseJSON["name"]

if __name__ == '__main__':
    unittest.main()
