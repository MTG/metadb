CREATE TABLE recording (
  mbid          UUID NOT NULL,
  added         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recording_release_group (
  recording_mbid      UUID NOT NULL,
  release_group_mbid  UUID NOT NULL
);

CREATE TABLE release_group (
  mbid            UUID NOT NULL
);

CREATE TABLE release_group_meta (
  mbid               UUID NOT NULL,
  name               TEXT,
  artist_credit      TEXT,
  first_release_date TEXT,
  last_updated       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recording_meta (
  mbid            UUID NOT NULL,
  name            TEXT,
  artist_credit   TEXT,
  last_updated    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE source (
  id          SERIAL,
  name        TEXT
);

CREATE TABLE scraper (
  id          SERIAL,
  source_id   INTEGER NOT NULL, -- FK to source.id
  module      TEXT, -- python module name
  version     TEXT, -- anything
  description TEXT, -- anything
  added       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE item (
  id          SERIAL,
  mbid        UUID    NOT NULL, -- FK to recording.mbid or release_group.mbid
  scraper_id  INTEGER NOT NULL, -- FK to scraper.id
  added       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE item_data (
  item_id     INTEGER  NOT NULL, -- FK to item.id
  data        JSONB
);

CREATE TABLE token (
  token UUID    NOT NULL,
  admin BOOLEAN DEFAULT 'f',
  added         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
