BEGIN;

ALTER TABLE scraper
  ADD CONSTRAINT scraper_fk_source
  FOREIGN KEY (source_id)
    REFERENCES source (id);

ALTER TABLE item
  ADD CONSTRAINT item_fk_scraper
  FOREIGN KEY (scraper_id)
    REFERENCES scraper (id);

ALTER TABLE item_data
  ADD CONSTRAINT item_data_fk_item
  FOREIGN KEY (item_id)
    REFERENCES item (id);

COMMIT;
