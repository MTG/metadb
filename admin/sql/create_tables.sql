BEGIN;

CREATE TABLE mbids (
  mbid        UUID NOT NULL,
  added       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE source (
  id          SERIAL,
  name        TEXT
);

CREATE TABLE scraper (
  id          SERIAL,
  source_id   INTEGER NOT NULL, -- FK to source.id
  version     TEXT,
  description TEXT
);

CREATE TABLE item (
  id          SERIAL,
  mbid        UUID    NOT NULL,
  scraper_id  INTEGER NOT NULL, -- FK to scraper.id
  added       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE item_data (
  item_id     INTEGER  NOT NULL, -- FK to item.id
  data        JSONB,
  request     TEXT,
  response    TEXT
);

COMMIT;
