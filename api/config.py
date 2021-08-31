import logging
from logging.handlers import TimedRotatingFileHandler
import pathlib
import os
import sys
from logging.config import fileConfig

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCEPTABLE_MODEL_DIFFERENCE = 0.2
APP_NAME = 'ml_api'

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s —"
    "%(funcName)s:%(lineno)d — %(message)s")
LOG_DIR = PACKAGE_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'ml_api.log'
UPLOAD_FOLDER = PACKAGE_ROOT / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SERVER_PORT = 5000
    UPLOAD_FOLDER = UPLOAD_FOLDER
    SERVER_ADDRESS= os.environ.get('SERVER_ADDRESS', '0.0.0.0')
    SERVER_PORT= os.environ.get('SERVER_PORT', '5000')
    LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", logging.INFO)
    SHADOW_MODE_ACTIVE = os.getenv('SHADOW_MODE_ACTIVE', True)
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_PORT = os.getenv("DB_PORT", 6609)
    DB_HOST = os.getenv("DB_HOST", "database")
    DB_NAME = os.getenv("DB_NAME", "ml_api")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:"
        f"{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
class ProductionConfig(Config):
    DEBUG = False
    SERVER_ADDRESS= os.environ.get('SERVER_ADDRESS', '0.0.0.0')
    SERVER_PORT= os.environ.get('SERVER_PORT', '5000')

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

class TestingConfig(Config):
    TESTING = True
    LOGGING_LEVEL = logging.WARNING
    DB_USER = os.getenv("DB_USER", "user_test")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_PORT = os.getenv("DB_PORT", 6608)
    DB_HOST = os.getenv("DB_HOST", "database_test")
    DB_NAME = os.getenv("DB_NAME", "ml_api_test")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:"
        f"{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.WARNING)
    return file_handler


def get_logger(*, logger_name):
    """Get logger with prepared handlers."""

    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.INFO)

    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False

    return logger

def setup_app_logging(config: Config) -> None:
    """Prepare custom logging for our application."""
    _disable_irrelevant_loggers()
    fileConfig(PACKAGE_ROOT / 'gunicorn_logging.conf')
    logger = logging.getLogger('mlapi')
    logger.setLevel(config.LOGGING_LEVEL)


def _disable_irrelevant_loggers() -> None:
    """Disable loggers created by packages which create a lot of noise."""
    for logger_name in (
        "connexion.apis.flask_api",
        "connexion.apis.abstract",
        "connexion.decorators",
        "connexion.operation",
        "connexion.operations",
        "connexion.app",
        "openapi_spec_validator",
    ):
        logging.getLogger(logger_name).level = logging.WARNING




