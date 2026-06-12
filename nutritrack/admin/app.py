from flask import Flask
from nutritrack.api.settings import get_settings
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = settings.secret_key

    from nutritrack.admin.routes import bp

    app.register_blueprint(bp)

    logger.info("Flask admin app created")
    return app
