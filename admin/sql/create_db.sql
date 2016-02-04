\set ON_ERROR_STOP 1

-- Create the user and the database. Must run as user postgres.

CREATE USER metadb NOCREATEDB NOCREATEUSER;
CREATE DATABASE metadb WITH OWNER = metadb TEMPLATE template0 ENCODING = 'UNICODE';
