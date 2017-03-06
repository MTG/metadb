-- Create the user and the database. Must run as user postgres.

CREATE USER metadb NOCREATEDB NOSUPERUSER;
ALTER USER metadb SET SEARCH_PATH TO metadb;
CREATE DATABASE metadb WITH OWNER = metadb TEMPLATE template0 ENCODING = 'UNICODE';
