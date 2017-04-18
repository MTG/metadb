
from webserver import create_app
import os
import click
import config
import csv
import sys

from metadb import db
from metadb import data

ADMIN_SQL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'admin', 'sql')

cli = click.Group()


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", show_default=True)
@click.option("--port", "-p", default=8080, show_default=True)
def runserver(host, port):
    create_app().run(host=host, port=port)


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Drop existing database and user.")
def init_db(force):
    """Initializes database.

    This process involves several steps:
    1. Table structure is created.
    2. Primary keys and foreign keys are created.
    3. Indexes are created.
    """

    db.init_db_engine(config.SQLALCHEMY_ADMIN_URI)
    if force:
        print('Dropping existing database...')
        res = db.run_sql_script_without_transaction(os.path.join(ADMIN_SQL_DIR, 'drop_db.sql'))
        if not res:
            sys.exit(1)

    print('Creating user and a database...')
    res = db.run_sql_script_without_transaction(os.path.join(ADMIN_SQL_DIR, 'create_db.sql'))
    if not res:
        sys.exit(1)
    db.engine.dispose()

    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    print('Creating tables...')
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_schema.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_types.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_tables.sql'))

    print('Creating primary and foreign keys...')
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_primary_keys.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_foreign_keys.sql'))

    print('Creating indexes...')
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_indexes.sql'))

    print("Done!")


@cli.command()
@click.option("--force", "-f", is_flag=True, help="Drop existing database and user.")
def init_test_db(force=False):
    """Same as `init_db` command, but creates a database that will be used to run tests.

    `SQLALCHEMY_TEST_URI` variable must be defined in the config file.
    """

    db.init_db_engine(config.SQLALCHEMY_ADMIN_URI)
    if force:
        print('Dropping existing test database...')
        res = db.run_sql_script_without_transaction(os.path.join(ADMIN_SQL_DIR, 'drop_test_db.sql'))
        if not res:
            sys.exit(1)

    print('Creating database and user for testing...')
    res = db.run_sql_script_without_transaction(os.path.join(ADMIN_SQL_DIR, 'create_test_db.sql'))
    if not res:
        sys.exit(1)
    db.engine.dispose()

    db.init_db_engine(config.SQLALCHEMY_TEST_URI)

    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_schema.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_types.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_tables.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_primary_keys.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_foreign_keys.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_indexes.sql'))

    print("Done!")

@cli.command()
def fixtures():
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    sources = os.path.join("fixtures", "sources")
    with open(sources) as fp:
        r = csv.DictReader(fp)
        for line in r:
            if not data.load_source(**line):
                data.add_source(**line)

    scrapers = os.path.join("fixtures", "scrapers")
    with open(scrapers) as fp:
        r = csv.DictReader(fp)
        for line in r:
            sname = line.pop("source")
            source = data.load_source(sname)
            line["source"] = source
            data.add_scraper(**line)

@cli.command()
@click.option("--admin", is_flag=True, help="Set if this token is for an admin")
def addtoken(admin):
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    token = data.add_token(admin)
    print("Added token: %s" % token)

@cli.command()
@click.argument("token")
def rmtoken(token):
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    data.remove_token(token)


@cli.command()
def lstokens():
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    tokens = data.get_tokens()

    for t in tokens:
        print("%s admin=%s" % (t["token"], t["admin"]))

if __name__ == '__main__':
    cli()
