import connexion
import logging
from sqlalchemy.orm import scoped_session

from api.config import get_logger
from api.persistence.core import init_database
from api.monitoring.middleware import setup_metrics

_logger = logging.getLogger('mlapi')

def create_app(*, config_object,db_session= None):
    """ Create a flask app instance
    
    Parameters
    ----------
    config_object : api.config.Config class type 
    db_session : scoped_session class type 

    """
    connexion_app = connexion.App(
        __name__, debug=config_object.DEBUG, specification_dir="spec/"
    )

    flask_app = connexion_app.app
    flask_app.config.from_object(config_object)
    # Instantiating the database
    # Setup database
    init_database(flask_app, config=config_object,db_session=db_session)
    # Setup prometheus monitoring
    setup_metrics(flask_app)

    connexion_app.add_api("api.yml")

    # logging
    _logger.debug("Application instance created")

    return connexion_app

