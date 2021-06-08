import pytest

from api.app import create_app
from api.config import TestingConfig


@pytest.fixture
def app():
    """ The fixture that create an application in test mode with its own context 
    
    Returns
    -------
    fask application object 
        A flask application object in test mode is yielded
    """

    app = create_app(config_object=TestingConfig).app

    with app.app_context():
        yield app

@pytest.fixture
def flask_test_client(app):
    """ A flask test client 
    
    Parameters
    ----------
    app : a flask application object
        A flask application object with the config.TESTING configuration with it's own context as we
        will be calling the fixture app to feed as this function input.
    
    Returns
    -------
    test_client: app.test_client
         yield an app.test_client object
    """

    with app.test_client() as test_client:
        yield test_client
