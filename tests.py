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
        db.drop_collection('users')

    # Test auth
    def test_register_user(self):
        response = self.app.post('/register/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'user' in responseJSON["username"]

    def test_auth_user(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'user' in responseJSON["username"]

    def test_unauthorized_user(self):
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="something",
                                     password="wrong"
                                     )),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)

    # Trip tests
    def test_create_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        username = responseJSON["username"]
        token = responseJSON["token"]
        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A Trip' in responseJSON["name"]
        assert 'user' in responseJSON["username"]

    def test_update_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.put('/trips/'+postedObjectID,
                                data=json.dumps(dict(
                                    name="An Updated Trip",
                                    username=username,
                                    token=token
                                    )),
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'An Updated Trip' in responseJSON["name"]

    def test_update_unauth(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user1",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user1",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username1 = responseJSON["username"]
        token1 = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.put('/trips/'+postedObjectID,
                                data=json.dumps(dict(
                                    name="An Updated Trip",
                                    username=username1,
                                    token=token1
                                    )),
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 401)

    def test_update_non_existent_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.put('/trips/55f0cbb4236f44b7f0e3cb23',
                                data=json.dumps(dict(
                                    name="An Updated Trip",
                                    username=username,
                                    token=token
                                    )),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/'+postedObjectID,
                                   data=json.dumps(dict(
                                       username=username,
                                       token=token
                                       )),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type

    def test_delete_unauth(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user1",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user1",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username1 = responseJSON["username"]
        token1 = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/'+postedObjectID,
                                   data=json.dumps(dict(
                                       username=username1,
                                       token=token1
                                       )),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_delete_non_existent_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.delete('/trips/55f0cbb4236f44b7f0e3cb23',
                                   data=json.dumps(dict(
                                       username=username,
                                       token=token
                                   )),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_get_trip_by_id(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID,
                                data=json.dumps(dict(
                                    username=username,
                                    token=token
                                    )),
                                content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'A Trip' in responseJSON["name"]

    def test_get_trip_unauth(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user1",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user1",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username1 = responseJSON["username"]
        token1 = responseJSON["token"]

        response = self.app.post('/trips/',
                                 data=json.dumps(dict(
                                     name="A Trip",
                                     username=username,
                                     token=token
                                     )),
                                 content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID,
                                data=json.dumps(dict(
                                    username=username1,
                                    token=token1
                                    )),
                                content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 401)

    def test_get_non_existent_trip(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23',
                                data=json.dumps(dict(
                                    username=username,
                                    token=token
                                    )),
                                content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_get_all_trips_for_user(self):
        self.app.post('/register/',
                      data=json.dumps(dict(
                          username="user",
                          password="pass"
                          )),
                      content_type='application/json')
        response = self.app.post('/login/',
                                 data=json.dumps(dict(
                                     username="user",
                                     password="pass"
                                     )),
                                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        username = responseJSON["username"]
        token = responseJSON["token"]

        self.app.post('/trips/',
                      data=json.dumps(dict(
                          name="A Trip",
                          username=username,
                          token=token
                          )),
                      content_type='application/json')
        self.app.post('/trips/',
                      data=json.dumps(dict(
                          name="Another Trip",
                          username=username,
                          token=token
                          )),
                      content_type='application/json')
        response = self.app.get('/trips/',
                                data=json.dumps(dict(
                                    username=username,
                                    token=token
                                    )),
                                content_type="application/json")

        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert 'Another Trip' in responseJSON[1]["name"]

if __name__ == '__main__':
    unittest.main()
