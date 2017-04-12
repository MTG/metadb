from celery import Celery
from webserver import create_app

import metadb.scrapers
from metadb import data
from metadb import db


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    db.init_db_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = create_app(web=False)
celery = make_celery(app)


# TODO Have a custom task runner to dispose of database connections even if we raise an exception
# TODO: Or, just try/catch the exception in the correct place??
@celery.task()
def scrape_musicbrainz(recording_mbid):
    """

    :param recording_mbid:
    :return:
    """

    source = data.load_source("musicbrainz")
    scrapers = data.load_scrapers_for_source(source)
    if scrapers:
        s = scrapers[0]
        s_obj = metadb.scrapers.create_scraper_object(s)
        if s_obj:
            s_obj.config()
            result = s_obj.scrape({"mbid": recording_mbid})
            if result:
                data.add_item(s, recording_mbid, data=result)
                data.cache_musicbrainz_metadata(result)
            s_obj.dispose()
