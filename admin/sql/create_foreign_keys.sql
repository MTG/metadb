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

ALTER TABLE recording_release_group
  ADD CONSTRAINT recording_release_group_fk_recording
  FOREIGN KEY (recording_mbid)
    REFERENCES recording (mbid);

ALTER TABLE recording_release_group
  ADD CONSTRAINT recording_release_group_fk_release_group
  FOREIGN KEY (release_group_mbid)
    REFERENCES release_group (mbid);

ALTER TABLE recording_meta
  ADD CONSTRAINT recording_meta_fk_recording
  FOREIGN KEY (mbid)
    REFERENCES recording (mbid);

ALTER TABLE release_group_meta
  ADD CONSTRAINT release_group_meta_fk_release_group
  FOREIGN KEY (mbid)
    REFERENCES release_group (mbid);