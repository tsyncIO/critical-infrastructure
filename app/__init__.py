from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

# Always load .env from the project root, regardless of cwd
_ENV_FILE = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=_ENV_FILE)  # load .env before evaluating config

from .extensions import db, migrate
from .routes.pages import pages_bp
from .routes.api import api_bp
from config.flask_config import FlaskConfig
from .cli import kritis_cli

def create_app(config_object=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_object or FlaskConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.cli.add_command(kritis_cli)

    return app
