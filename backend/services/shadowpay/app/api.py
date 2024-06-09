from flask import Flask

from app.controllers.skin_controller import skin_controller
from app.controllers.status_controller import status_controller


def create_app():
    app = Flask(__name__)
    app.register_blueprint(skin_controller)
    app.register_blueprint(status_controller)
    return app
