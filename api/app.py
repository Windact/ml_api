from flask import Flask

from api.config import get_logger

_logger = get_logger(logger_name=__name__)

def create_app(*, config_object):
    """ Create a flask app instance """

    flask_app = Flask("ml_api")
    # Adding the config to the flask app instance
    flask_app.config.from_object(config_object)

    # import blueprints
    from api.controller import prediction_app
    flask_app.register_blueprint(prediction_app)
    # logging
    _logger.debug("Application instance created")

    return flask_app