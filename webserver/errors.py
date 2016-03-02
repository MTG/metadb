from flask import render_template
import webserver.exceptions


def init_error_handlers(app):

    @app.errorhandler(webserver.exceptions.APIError)
    def api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

