from flask import jsonify

import webserver.exceptions


def init_error_handlers(app):

    @app.errorhandler(webserver.exceptions.APIError)
    def api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(400)
    def bad_request(error):
        response = jsonify({"error": error.description})
        response.status_code = 400
        return response

    @app.errorhandler(401)
    def bad_request(error):
        response = jsonify({"error": error.description})
        response.status_code = 401
        return response

    @app.errorhandler(403)
    def bad_request(error):
        response = jsonify({"error": error.description})
        response.status_code = 403
        return response

