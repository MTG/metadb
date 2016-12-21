from metadb.testing import DatabaseTestCase
from metadb import data


class StatsDatabaseTestCase(DatabaseTestCase):
    def test_add_token(self):

        all_tokens = data.get_tokens()
        self.assertEqual(0, len(all_tokens))
        token = data.add_token()
        all_tokens = data.get_tokens()
        self.assertEqual({"token": str(token), "admin": False}, all_tokens[0])