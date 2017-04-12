ALTER TABLE recording ADD CONSTRAINT recording_pkey PRIMARY KEY (mbid);
ALTER TABLE recording_meta ADD CONSTRAINT recording_meta_pkey PRIMARY KEY (mbid);
ALTER TABLE release_group ADD CONSTRAINT release_group_pkey PRIMARY KEY (mbid);
ALTER TABLE release_group_meta ADD CONSTRAINT release_group_meta_pkey PRIMARY KEY (mbid);

ALTER TABLE source ADD CONSTRAINT source_pkey PRIMARY KEY (id);
ALTER TABLE scraper ADD CONSTRAINT scraper_pkey PRIMARY KEY (id);
ALTER TABLE item ADD CONSTRAINT item_pkey PRIMARY KEY (id);
ALTER TABLE item_data ADD CONSTRAINT item_data_pkey PRIMARY KEY (item_id);
