import logging
from logging.handlers import RotatingFileHandler, SMTPHandler


def init_loggers(app):
    if "LOG_FILE_ENABLED" in app.config and app.config["LOG_FILE_ENABLED"]:
        _add_file_handler(app, app.config["LOG_FILE"], level=logging.INFO)
    if "LOG_SENTRY_ENABLED" in app.config and app.config["LOG_SENTRY_ENABLED"]:
        _add_sentry(app, logging.INFO)


def _add_file_handler(app, filename, max_bytes=512 * 1024, backup_count=100,
                      level=logging.NOTSET):
    """Adds file logging."""
    file_handler = RotatingFileHandler(filename, maxBytes=max_bytes,
                                       backupCount=backup_count)
    file_handler.setLevel(level)
    app.logger.addHandler(file_handler)


def _add_sentry(app, level=logging.NOTSET):
    from raven.contrib.flask import Sentry
    """Adds support for error logging and aggregation using Sentry platform.

    See https://docs.getsentry.com for more information about it.
    """
    Sentry(app, logging=True, level=level)
