import os
from flask import Flask
from .views import views


def create_app():
    """Application factory used by the API entry point."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

    # Register all HTTP routes (UI + API) from the shared blueprint.
    app.register_blueprint(views, url_prefix="/")

    return app
