from metadb.testing import DatabaseTestCase
from metadb import data

import datetime
import pytz
import uuid
import mock


class DataTestCase(DatabaseTestCase):

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


class MusicBrainzMetaTestCase(DatabaseTestCase):
    """Tests for the metadata tables
    recording_meta, recording_release_group, release_group, release_group_meta"""

    def test_add_recording_doesnt_exist(self):
        """Check that if metadata for a recording doesn't exist, it's added"""
        mbid = str(uuid.uuid4())
        existing = data.get_recording_meta(mbid)
        self.assertIsNone(existing)

        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        meta = {"mbid": mbid, "name": "A song",
                "artist_credit": "An artist", "last_updated": now}

        data.add_recording_mbids([mbid])
        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, meta)

        new = data.get_recording_meta(mbid)
        self.assertEquals(new, meta)

    def test_add_recording_exists_uptodate(self):
        """Check that if recording metdata already exists and it is up-to-date,
        that it is not updated"""
        mbid = str(uuid.uuid4())
        updated = datetime.datetime(2017, 4, 4, 10, 20, 30, tzinfo=pytz.utc)
        meta = {"mbid": mbid, "name": "A song",
                "artist_credit": "An artist", "last_updated": updated}

        # Add the data to the database
        data.add_recording_mbids([mbid])
        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, meta)

        get = mock.Mock()
        _get_recording_meta = data._get_recording_meta
        get.return_value = meta
        data._get_recording_meta = get

        mockconn = mock.MagicMock()
        mockexec = mock.Mock()
        mockconn.execute = mockexec

        # Adding a recording with the same date as the existing row results in no update
        data._add_recording_meta(mockconn, meta)
        get.assert_called_once_with(mockconn, mbid)
        mockexec.assert_not_called()

        # A recording with an earlier date results in no update
        get.reset_mock()
        updated = datetime.datetime(2017, 4, 4, 3, 20, 30, tzinfo=pytz.utc)
        meta["last_updated"] = updated
        data._add_recording_meta(mockconn, meta)
        get.assert_called_once_with(mockconn, mbid)
        mockexec.assert_not_called()

        data._get_recording_meta = _get_recording_meta

    def test_add_recording_exists_out_of_date(self):
        """Check that if recording metdata already exists and it is out of date
        that it is changed"""

        mbid = str(uuid.uuid4())
        now = datetime.datetime(2017, 4, 2, 10, 43, 0, tzinfo=pytz.utc)
        meta = {"mbid": mbid, "name": "A song",
                "artist_credit": "An artist", "last_updated": now}

        data.add_recording_mbids([mbid])
        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, meta)

        original_meta = data.get_recording_meta(mbid)
        self.assertIsNotNone(original_meta)

        # This is later than the last_updated date on the previous data
        newnow = datetime.datetime(2017, 4, 5, 10, 43, 0, tzinfo=pytz.utc)
        newmeta = {"mbid": mbid, "name": "New song title",
                   "artist_credit": "A different artist credit", "last_updated": newnow}

        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, newmeta)

        updated_meta = data.get_recording_meta(mbid)
        self.assertEqual(updated_meta, newmeta)

    def test_add_recording_exists_up_to_date_timezone(self):
        """Check that the test for up-to-dateness takes timezones into consideration"""

        mbid = str(uuid.uuid4())
        now = datetime.datetime(2017, 4, 2, 10, 43, 0, tzinfo=pytz.utc)
        meta = {"mbid": mbid, "name": "A song",
                "artist_credit": "An artist", "last_updated": now}

        data.add_recording_mbids([mbid])
        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, meta)

        original_meta = data.get_recording_meta(mbid)
        self.assertIsNotNone(original_meta)

        # This is 1h30m ahead of the original date, but on this date DST was in effect
        # and CEST is 2h ahead of UTC. This will not update
        tz = pytz.timezone("Europe/Madrid")
        newnow = tz.localize(datetime.datetime(2017, 4, 2, 12, 13, 0))
        newmeta = {"mbid": mbid, "name": "New song title",
                   "artist_credit": "A different artist credit", "last_updated": newnow}

        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, newmeta)

        not_updated_meta = data.get_recording_meta(mbid)
        self.assertEqual(not_updated_meta, meta)

    def test_releasegroup_doesnt_exist(self):
        """ Release group doesn't exist - gets added"""

        rgmbid = str(uuid.uuid4())

        existing = data.get_release_group_meta(rgmbid)
        self.assertIsNone(existing)

        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        meta = {"mbid": rgmbid, "name": "A release", "artist_credit": "Some artist",
                "first_release_date": "2012-03", "last_updated": now}

        with data.db.engine.connect() as connection:
            data._add_release_group_meta(connection, meta)

        new = data.get_release_group_meta(rgmbid)
        self.assertEqual(meta, new)

    def test_releasegroup_exists_up_to_date(self):
        """A release group exists and last_updated hasn't changed, doesn't result in an update"""

        rgmbid = str(uuid.uuid4())
        updated = datetime.datetime(2017, 4, 4, 10, 20, 30, tzinfo=pytz.utc)
        meta = {"mbid": rgmbid, "name": "A release", "artist_credit": "Some artist",
                "first_release_date": "2012-03", "last_updated": updated}

        # Add the data to the database
        with data.db.engine.begin() as connection:
            data._add_release_group_meta(connection, meta)

        get = mock.Mock()
        _get_release_group_meta = data._get_release_group_meta
        get.return_value = meta
        data._get_release_group_meta = get

        mockconn = mock.MagicMock()
        mockexec = mock.Mock()
        mockconn.execute = mockexec

        # Adding a recording with the same date as the existing row results in no update
        data._add_release_group_meta(mockconn, meta)
        get.assert_called_once_with(mockconn, rgmbid)
        mockexec.assert_not_called()

        # A recording with an earlier date results in no update
        get.reset_mock()
        updated = datetime.datetime(2017, 4, 4, 3, 20, 30, tzinfo=pytz.utc)
        meta["last_updated"] = updated
        data._add_release_group_meta(mockconn, meta)
        get.assert_called_once_with(mockconn, rgmbid)
        mockexec.assert_not_called()

        data._get_release_group_meta = _get_release_group_meta

    def test_releasegroup_exists_out_of_date(self):
        """Release group exists but last_updated is newer"""
        rgmbid = str(uuid.uuid4())

        now = datetime.datetime(2017, 4, 4, 3, 20, 30, tzinfo=pytz.utc)
        meta = {"mbid": rgmbid, "name": "A release", "artist_credit": "Some artist",
                "first_release_date": "2012-03", "last_updated": now}

        with data.db.engine.connect() as connection:
            data._add_release_group_meta(connection, meta)

        new = data.get_release_group_meta(rgmbid)
        self.assertEqual(new, meta)

        newnow = datetime.datetime(2017, 4, 10, 13, 20, 30, tzinfo=pytz.utc)
        newmeta = {"mbid": rgmbid, "name": "A changed release",
                   "artist_credit": "Some updated artist",
                   "first_release_date": "2012-02", "last_updated": newnow}

        with data.db.engine.connect() as connection:
            data._add_release_group_meta(connection, newmeta)

        new = data.get_release_group_meta(rgmbid)
        self.assertEqual(new, newmeta)

    def test_releasegroup_add_mapping(self):

        recmbid1 = str(uuid.uuid4())
        recmbid2 = str(uuid.uuid4())
        recmbid3 = str(uuid.uuid4())
        rgmbid1 = str(uuid.uuid4())
        rgmbid2 = str(uuid.uuid4())
        with data.db.engine.connect() as connection:
            connection.execute("INSERT INTO release_group (mbid) VALUES (%s), (%s)", (rgmbid1, rgmbid2))
        data.add_recording_mbids([recmbid1, recmbid2, recmbid3])

        rgs = data.get_release_groups_for_recording(recmbid1)
        self.assertEqual(len(rgs), 0)

        with data.db.engine.connect() as connection:
            data._add_link_recording_release_group(connection, recmbid1, rgmbid1)
            data._add_link_recording_release_group(connection, recmbid2, rgmbid1)
            data._add_link_recording_release_group(connection, recmbid2, rgmbid2)
            data._add_link_recording_release_group(connection, recmbid3, rgmbid2)

        rgs = data.get_release_groups_for_recording(recmbid1)
        self.assertEqual(rgs, [rgmbid1])
        rgs = data.get_release_groups_for_recording(recmbid2)
        self.assertEqual(rgs, [rgmbid1, rgmbid2])
        rgs = data.get_release_groups_for_recording(recmbid3)
        self.assertEqual(rgs, [rgmbid2])
