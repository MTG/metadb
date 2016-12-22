from metadb.testing import DatabaseTestCase
from metadb import data


class StatsDatabaseTestCase(DatabaseTestCase):

    def test_add_recording_mbids(self):
        recordings = data.get_recording_mbids()
        self.assertEqual(0, len(recordings))

        data.add_recording_mbids(["232ecd2b-7369-41a8-be13-1ed34c3712f7", "10da17c9-3e8a-4268-87ca-ccf52a91bd6d"])
        recordings = data.get_recording_mbids()
        self.assertEqual(2, len(recordings))

        # Try and add an existing recording skips it
        data.add_recording_mbids(["10da17c9-3e8a-4268-87ca-ccf52a91bd6d", "9814edcf-24a2-4ef7-bd04-8db0dddaf575"])
        recordings = data.get_recording_mbids()
        self.assertEqual(3, len(recordings))
