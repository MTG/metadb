from metadb.testing import DatabaseTestCase
from metadb import data


class StatsDatabaseTestCase(DatabaseTestCase):

    def test_add_token(self):
        all_tokens = data.get_tokens()
        self.assertEqual(0, len(all_tokens))
        token = data.add_token()
        all_tokens = data.get_tokens()
        self.assertEqual({"token": str(token), "admin": False}, all_tokens[0])

        # Admin token
        admintoken = data.add_token(True)
        all_tokens = data.get_tokens()
        self.assertEqual({"token": str(admintoken), "admin": True}, all_tokens[1])

    def test_get_token(self):
        # A token that exists is returned
        token = data.add_token()

        newtoken = data.get_token(token)
        self.assertEqual({"token": str(token), "admin": False}, newtoken)

        # A token that doesn't exist returns empty
        notoken = data.get_token("02ce410a-8484-48cd-ad5b-6b5b57400a91")
        self.assertEqual({}, notoken)

        # A token that isn't a UUID returns empty
        notoken = data.get_token("not-a-uuid")
        self.assertEqual({}, notoken)

    def test_remove_token(self):
        all_tokens = data.get_tokens()
        self.assertEqual(0, len(all_tokens))
        token = data.add_token()
        all_tokens = data.get_tokens()
        self.assertEqual(1, len(all_tokens))

        # A token that doesn't exist isn't remove
        data.remove_token("02ce410a-8484-48cd-ad5b-6b5b57400a91")
        all_tokens = data.get_tokens()
        self.assertEqual(1, len(all_tokens))

        # An invalid token does nothing
        data.remove_token("not-a-token")
        all_tokens = data.get_tokens()
        self.assertEqual(1, len(all_tokens))

        # Removing a token
        data.remove_token(token)
        all_tokens = data.get_tokens()
        self.assertEqual(0, len(all_tokens))