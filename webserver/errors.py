from flask import render_template


def init_error_handlers(app):

    @app.errorhandler(webserver.exceptions.APIError)
    def api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

