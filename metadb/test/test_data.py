from metadb.testing import DatabaseTestCase
from metadb import data

import datetime
import pytz
import uuid
import mock
import copy


class DataTestCase(DatabaseTestCase):

    def test_add_scraper(self):
        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "0.1", "desc")

        getscraper = data.load_scrapers_for_source(source)
        self.assertEqual(len(getscraper), 1)
        self.assertEqual(getscraper[0], scraper)

    def test_load_latest_scraper(self):
        source = data.add_source("test_source")
        scrapernew = data.add_scraper(source, "module", "recording", "0.2", "desc")
        scraperold = data.add_scraper(source, "module", "recording", "0.1", "desc")

        # Even though we added them in the "wrong" order, latest is based on version number
        getscraper = data.load_latest_scraper_for_source(source)
        self.assertEqual(getscraper, scrapernew)

    def test_load_latest_scraper_doesnt_exist(self):
        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "0.2", "desc")

        other_source = data.add_source("other_source")
        getscraper = data.load_latest_scraper_for_source(other_source)
        self.assertIsNone(getscraper)

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

    def test_add_item(self):
        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "version", "desc")

        mbid = "e644e49b-1576-4ef2-b340-147590e9e5ac"
        payload = {"test": "data"}

        res = data.add_item(scraper, mbid, payload)
        self.assertEqual(res, True)
        # Can get the item
        item = data.load_item(mbid, "test_source")
        self.assertEqual(item["data"], payload)

        # Adding the item again does nothing
        res = data.add_item(scraper, mbid, payload)
        self.assertEqual(res, False)

    def test_add_item_no_data(self):
        """Adding an item with no data will add an item row but no
           item_data, causing load_item to return nothing."""
        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "version", "desc")

        mbid = "e644e49b-1576-4ef2-b340-147590e9e5ac"

        res = data.add_item(scraper, mbid, {})
        # return value says we added something
        self.assertTrue(res)
        # but there is no data
        item = data.load_item(mbid, "test_source")
        self.assertIsNone(item["data"])

    def test_get_recordings_missing_meta(self):
        mbids = ["f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9", "4410602a-7ecc-43a3-94d0-cae6905dffa4",
                 "77a81b61-da0e-451a-8b53-47d396946285"]
        data.add_recording_mbids(mbids)

        missing = data.get_recordings_missing_meta()
        self.assertCountEqual(missing, mbids)

        recording = {"mbid": "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9",
                     "name": "name",
                     "artist_credit": "credit",
                     "last_updated": datetime.datetime.now()}
        with data.db.engine.begin() as connection:
            data._add_recording_meta(connection, recording)

        missing = data.get_recordings_missing_meta()
        self.assertCountEqual(missing, ["4410602a-7ecc-43a3-94d0-cae6905dffa4", "77a81b61-da0e-451a-8b53-47d396946285"])

        # Add a redirect
        data.musicbrainz_check_mbid_redirect("4410602a-7ecc-43a3-94d0-cae6905dffa4", "77a81b61-da0e-451a-8b53-47d396946285")

        missing = data.get_recordings_missing_meta()
        print(missing)
        self.assertCountEqual(missing, ["77a81b61-da0e-451a-8b53-47d396946285"])


class ScraperTestCase(DatabaseTestCase):
    def test_get_unprocessed_recordings(self):
        mbids = ["f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9", "4410602a-7ecc-43a3-94d0-cae6905dffa4",
                 "77a81b61-da0e-451a-8b53-47d396946285"]
        data.add_recording_mbids(mbids)
        now = datetime.datetime.now()
        meta = [{"mbid": "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9",
                 "name": "trackname1",
                 "artist_credit": "test_artist_name1",
                 "last_updated": now},
                {"mbid": "4410602a-7ecc-43a3-94d0-cae6905dffa4",
                 "name": "trackname2",
                 "artist_credit": "test_artist_2",
                 "last_updated": now},
                {"mbid": "77a81b61-da0e-451a-8b53-47d396946285",
                 "name": "trackname3",
                 "artist_credit": "test_artist_2",
                 "last_updated": now}]
        with data.db.engine.begin() as connection:
            for m in meta:
                data._add_recording_meta(connection, m)

        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "0.1", "desc")

        def get_meta_for_mbid(mbid):
            item = [i for i in meta if i["mbid"] == mbid][0]
            item = copy.deepcopy(item)
            item.pop("last_updated")
            return item

        unprocessed = data.get_unprocessed_recordings_for_scraper(scraper)
        self.assertEqual(len(unprocessed), 3)
        self.assertEqual(get_meta_for_mbid(unprocessed[0]["mbid"]), unprocessed[0])
        self.assertEqual(get_meta_for_mbid(unprocessed[1]["mbid"]), unprocessed[1])
        self.assertEqual(get_meta_for_mbid(unprocessed[2]["mbid"]), unprocessed[2])

        # Add some data for one mbid
        data.add_item(scraper, "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9", {"test": "data"})
        unprocessed = data.get_unprocessed_recordings_for_scraper(scraper)
        self.assertCountEqual(["4410602a-7ecc-43a3-94d0-cae6905dffa4",
                               "77a81b61-da0e-451a-8b53-47d396946285"], [u["mbid"] for u in unprocessed])

        # Make one of the mbids a redirect
        data.musicbrainz_check_mbid_redirect("4410602a-7ecc-43a3-94d0-cae6905dffa4",
                                             "77a81b61-da0e-451a-8b53-47d396946285")
        unprocessed = data.get_unprocessed_recordings_for_scraper(scraper)
        self.assertCountEqual(["77a81b61-da0e-451a-8b53-47d396946285"], [u["mbid"] for u in unprocessed])

    def test_get_unprocessed_recordings_no_id(self):
        """If we ask for unprocessed recordings and specify an ID which isn't in the
           database, (or is already processed???), it returns nothing"""

        mbids = ["f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9", "4410602a-7ecc-43a3-94d0-cae6905dffa4"]
        data.add_recording_mbids(mbids)
        now = datetime.datetime.now()
        meta = [{"mbid": "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9",
                 "name": "trackname1",
                 "artist_credit": "test_artist_name1",
                 "last_updated": now}]
        with data.db.engine.begin() as connection:
            for m in meta:
                data._add_recording_meta(connection, m)

        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "recording", "0.1", "desc")
        data.add_item(scraper, "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9", {"test": "data"})

        # An mbid which already has data
        unprocessed = data.get_unprocessed_recordings_for_scraper(scraper, "f84ca3bf-e561-41bb-9ba3-f8b7d79e3af9")
        self.assertEqual(len(unprocessed), 0)

        # An mbid which isn't in the database
        unprocessed = data.get_unprocessed_recordings_for_scraper(scraper, "868bdb9d-508d-446d-913b-6c1bd18c7ef5")
        self.assertEqual(len(unprocessed), 0)

    def test_get_unprocessed_release_groups(self):
        now = datetime.datetime.now()
        meta = [{"mbid": "79333adb-bcde-4c7f-b204-918d5ca57f41",
                 "name": "rg_title1",
                 "artist_credit": "test_artist_name1",
                 "first_release_date": "2010",
                 "last_updated": now},
                {"mbid": "006eb612-908a-484e-bc8a-17b5882d35c1",
                 "name": "rg_title2",
                 "artist_credit": "test_artist_name2",
                 "first_release_date": "1995",
                 "last_updated": now}]
        with data.db.engine.begin() as connection:
            for m in meta:
                data._add_release_group_meta(connection, m)

        source = data.add_source("test_source")
        scraper = data.add_scraper(source, "module", "release_group", "0.1", "desc")

        unprocessed = data.get_unprocessed_release_groups_for_scraper(scraper)
        self.assertEqual(len(unprocessed), 2)

        del meta[0]["last_updated"]
        del meta[1]["last_updated"]
        self.assertCountEqual(unprocessed, meta)

        data.add_item(scraper, "79333adb-bcde-4c7f-b204-918d5ca57f41", {"test": "data"})

        unprocessed = data.get_unprocessed_release_groups_for_scraper(scraper)
        self.assertEqual(len(unprocessed), 1)
        self.assertCountEqual(unprocessed, [meta[1]])


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
