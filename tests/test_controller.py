import json

from classification_model.config.core import config
from classification_model import __version__ as _version
from classification_model.processing import utils
from api import __version__ as api_version

def test_version_endpoint(flask_test_client):
    """ Test version endpoint 

    Parameters
    ----------
    flask_test_client : app test_client object
    """

    #  When
    response = flask_test_client.get("/version")

    # Then
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json.get("model_verison") == _version
    assert response_json.get("api_version") == api_version


def test_pumps_endpoint_return_status(flask_test_client):
    """ Testing pumps route status return 
    
    Parameters
    ----------
    flask_test_client : app test_client object
    """

    #When
    response = flask_test_client.get("/pumps")

    # Then
    assert response.status_code == 200


def test_prediction_endpoint_returns_prediction(flask_test_client):
    """ TEST if the predict.make_prediction output have the expected ouputs and formats 
    
    Parameters
    ----------
    flask_test_client : app test_client object
    """

    test_data = utils.load_dataset(filename=config.app_config.TESTING_DATA_FILE)
    post_json = test_data.to_json(orient='records') 
    post_data = json.loads(post_json)

    # When
    response = flask_test_client.post("/v1/predict/classification",json=post_data)

    # Then
    assert response.status_code == 200
    response_json = json.loads(response.data)
    prediction = response_json.get("predictions")
    response_version = response_json.get("version")
    assert len(prediction) == test_data.shape[0]
    assert response_version == _version