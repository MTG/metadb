import json

from webserver import testing
import mock


class TestAuthentication(testing.ServerTestCase):

    @mock.patch("metadb.data.get_token")
    def test_unauthorized(self, get_token):
        # No auth header
        resp = self.client.post("/recordings")
        self.assertEqual(401, resp.status_code)

        # an auth header which doesn't exist
        get_token.return_value = {}
        id = "dae2d48f-d668-4f69-ba2b-22513bb60a8a"
        resp = self.client.post("/recordings", headers={"Authorization": "Token {}".format(id)})
        self.assertEqual(401, resp.status_code)
        expected = {"error": "The server could not verify that you are authorized to access the URL requested.  You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."}
        self.assertEquals(expected, resp.json)
        get_token.assert_called_once_with(id)

    @mock.patch("metadb.data.get_token")
    def test_admin(self, get_token):
        # The auth header returns that the user is an admin
        id = "dae2d48f-d668-4f69-ba2b-22513bb60a8a"
        get_token.return_value = {"token": id, "admin": True}
        resp = self.client.post("/recordings",
                                data=json.dumps([]),
                                content_type="application/json",
                                headers={"Authorization": "Token {}".format(id)})
        self.assertEqual(200, resp.status_code)
        get_token.assert_called_once_with(id)


class TestRecordingSubmit(testing.ServerTestCase):

    id = "dae2d48f-d668-4f69-ba2b-22513bb60a8a"

    def _submit(self, data):
        return self.client.post("/recordings",
                                data=json.dumps(data),
                                content_type="application/json",
                                headers={"Authorization": "Token {}".format(self.id)})

    @mock.patch("metadb.data.get_token")
    @mock.patch("metadb.data.add_recording_mbids")
    def test_bad_data(self, add_recording_mbids, get_token):
        # No content type
        get_token.return_value = get_token.return_value = {"token": self.id, "admin": True}
        resp = self.client.post("/recordings",
                                data=json.dumps([]),
                                headers={"Authorization": "Token {}".format(self.id)})
        self.assertEqual(400, resp.status_code)
        self.assertEqual({"message": "Submitted data must be a list"}, resp.json)

        # If the json is not a list
        resp = self._submit({"not": "list"})
        self.assertEqual(400, resp.status_code)
        self.assertEqual({"message": "Submitted data must be a list"}, resp.json)


    @mock.patch("metadb.data.get_token")
    @mock.patch("metadb.data.add_recording_mbids")
    def test_skip_invalid(self, add_recording_mbids, get_token):
        # For any items in the list which are not valid uuids, skip
        get_token.return_value = get_token.return_value = {"token": self.id, "admin": True}

        data = ["e0efcfa8-0b4e-43e7-bae2-5feccf55045f", 1, "not", "924232e9-a1d6-45e9-aa1a-5de419c44921"]
        self._submit(data)

        expected = ["e0efcfa8-0b4e-43e7-bae2-5feccf55045f", "924232e9-a1d6-45e9-aa1a-5de419c44921"]
        add_recording_mbids.assert_called_once_with(expected)

    @mock.patch("metadb.data.get_token")
    @mock.patch("metadb.data.add_recording_mbids")
    def test_submit(self, add_recording_mbids, get_token):
        # Call correct submit method
        get_token.return_value = get_token.return_value = {"token": self.id, "admin": True}
        pass