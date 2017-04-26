import os

d = os.getenv("DEPLOY_ENV", "dev")
if d == "dev":
    DEBUG = True
elif d == "prod":
    DEBUG = False

SECRET_KEY = os.getenv("MDB_SECRET_KEY")
if not DEBUG and not SECRET_KEY:
    raise Exception("Must set a secret key in production mode")


# DATABASES
MUSICBRAINZ_DATABASE_URI = os.getenv("METADB_MUSICBRAINZ_DB_URI")

# Admin access
SQLALCHEMY_ADMIN_URI = os.getenv("METADB_ADMIN_URI")

# Primary database
SQLALCHEMY_DATABASE_URI = os.getenv("METADB_DB_URI")

# Database for testing
SQLALCHEMY_TEST_URI = os.getenv("METADB_TEST_DB_URI")

# LOGGING

LOG_FILE_ENABLED = False
LOG_FILE = "./metadb.log"

e = os.getenv("METADB_LOG_SENTRY_ENABLED")
LOG_SENTRY_ENABLED = e == "True"
SENTRY_DSN = os.getenv("METADB_SENTRY_DSN")

# MISCELLANEOUS

#BEHIND_GATEWAY = True
#REMOTE_ADDR_HEADER = "X-Remote-Addr"

CELERY_BROKER_URL = os.getenv("METADB_CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "redis://redis"
CELERY_ACCEPT_CONTENT = ['json']
