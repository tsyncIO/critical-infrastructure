from flask import Flask
from dotenv import load_dotenv
from .extensions import db, migrate
from .routes.pages import pages_bp
from .routes.api import api_bp
from config.flask_config import FlaskConfig
from .cli import kritis_cli


def create_app(config_object=None):
    load_dotenv()  # load .env or system env variables
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_object or FlaskConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.cli.add_command(kritis_cli)

    return app
