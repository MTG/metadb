from flask import Flask
from metadb import db
import sys
import os


def create_app(web=True):
    """ Create the flask app

    :param web: If True, this app is for the webserver, and should load blueprints and templating.
                Set to False for celery
    :return: the flask app
    """
    app = Flask(__name__)

    # Configuration
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
    import config
    app.config.from_object(config)

    # Logging
    from webserver.loggers import init_loggers
    init_loggers(app)

    # Extensions
    from flask_uuid import FlaskUUID
    FlaskUUID(app)

    # Error handling
    from webserver.errors import init_error_handlers
    init_error_handlers(app)

    if web:
        # Template utilities
        app.jinja_env.add_extension('jinja2.ext.do')
        from webserver import utils
        app.jinja_env.filters['date'] = utils.reformat_date
        app.jinja_env.filters['datetime'] = utils.reformat_datetime

        # Blueprints
        from webserver.views.index import index_bp
        from webserver.views.api import api_bp
        app.register_blueprint(index_bp)
        app.register_blueprint(api_bp)

    @app.before_request
    def before_request():
        db.init_db_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.engine.dispose()

    return app
