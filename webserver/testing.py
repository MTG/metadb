import flask_testing
from webserver import create_app


class ServerTestCase(flask_testing.TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app
