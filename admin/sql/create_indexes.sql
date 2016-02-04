BEGIN;

CREATE INDEX item_ndx_mbid ON item (mbid);
CREATE INDEX item_ndx_scraper_id ON item (scraper_id);
CREATE INDEX item_ndx_added ON item (added);

CREATE INDEX source_ndx_name ON source (name);
CREATE INDEX scraper_ndx_source_id ON scraper (source_id);

CREATE INDEX item_data_ndx_item_id ON item_data (item_id);

COMMIT;
