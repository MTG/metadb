-- Create the user and the database. Must run as user postgres.

CREATE USER mdb_test NOCREATEDB NOSUPERUSER;
CREATE DATABASE mdb_test WITH OWNER = mdb_test TEMPLATE template0 ENCODING = 'UNICODE';
