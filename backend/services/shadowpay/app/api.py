from flask import Flask
from app.controllers.skin_controller import skin_controller

def create_app():
    app = Flask(__name__)
    app.register_blueprint(skin_controller)
    return app
