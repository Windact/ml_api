import pytest
import os
from unittest import mock
from sqlalchemy_utils import create_database, database_exists

from classification_model.processing import utils
from classification_model.config.core import config as config_gbm


from api.app import create_app
from api.config import TestingConfig
from api.persistence import core




@pytest.fixture(scope='session')
def _db():
    db_url = TestingConfig.SQLALCHEMY_DATABASE_URI
    if not database_exists(db_url):
        create_database(db_url)
    # alembic can be configured through the configuration file. For testing
    # purposes 'env.py' also checks the 'ALEMBIC_DB_URI' variable first.
    engine = core.create_db_engine_from_config(config=TestingConfig())
    evars = {"ALEMBIC_DB_URI": db_url}
    #basicaly setting the ALEMBIC_DB_URI in the env to the db_url with the mock.patch.dict then I run the migrations to recreate my database tables
    with mock.patch.dict(os.environ, evars):
        core.run_migrations()
    
    yield engine

@pytest.fixture(scope='session')
def _db_session(_db):
    """ Create DB session for testing.
    """
    session = core.create_db_session(engine=_db)
    yield session


@pytest.fixture(scope='session')
def app(_db_session):
    """ The fixture that create an application in test mode with its own context 
    
    Returns
    -------
    fask application object 
        A flask application object in test mode is yielded
    """

    app = create_app(config_object=TestingConfig(), db_session=_db_session).app
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

@pytest.fixture
def test_inputs_df():
    # Load the gradient boosting test dataset which
    # is included in the model package
    # With deep=True (default), a new object will be created with a copy of the calling object’s data and indices. Modifications to the data or indices of the copy will not be reflected in the original object (see notes below).
    test_inputs_df = utils.load_dataset(filename= config_gbm.app_config.TESTING_DATA_FILE)
    return test_inputs_df.copy(deep=True)

