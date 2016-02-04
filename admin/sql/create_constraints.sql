BEGIN;

ALTER TABLE item
  ADD CONSTRAINT item_unique_mbid_scraper_id UNIQUE (mbid, scraper_id);

COMMIT;
