import logging
from logging.handlers import TimedRotatingFileHandler
import pathlib
import os
import sys

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCEPTABLE_MODEL_DIFFERENCE = 0.2

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
    LOGGING_LEVEL = logging.DEBUG

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
    root = logging.getLogger()
    root.setLevel(config.LOGGING_LEVEL)
    root.addHandler(get_console_handler())
    root.propagate = False


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




