import json
import pytest 
import time
from classification_model.config.core import config
from classification_model import __version__ as _version
from dl_classification_model import __version__ as nn_version

from classification_model.processing import utils
from api import __version__ as api_version
from api.persistence.models import NeuralNetModelPredictions, GradientBoostingModelPredictions

@pytest.mark.integration
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


@pytest.mark.integration
def test_pumps_endpoint_return_status(flask_test_client):
    """ Testing pumps route status return 
    
    Parameters
    ----------
    flask_test_client : app test_client object
    """

    #When
    response = flask_test_client.get("/")

    # Then
    assert response.status_code == 200

@pytest.mark.parametrize("api_endpoint,package_version",(("/v1/predictions/gbm",_version),("/v1/predictions/dl",nn_version)))
@pytest.mark.integration
def test_prediction_endpoint_returns_prediction(api_endpoint,package_version,flask_test_client,test_inputs_df):
    """ TEST if the predict.make_prediction output have the expected ouputs and formats 
    
    Parameters
    ----------
    flask_test_client : app test_client object
    """

    test_data = test_inputs_df
    post_json = test_data.to_json(orient='records') 
    post_data = json.loads(post_json)

    # When
    response = flask_test_client.post(api_endpoint,json=post_data)

    # Then
    assert response.status_code == 200
    response_json = json.loads(response.data)
    prediction = response_json.get("predictions")
    response_version = response_json.get("version")
    assert len(prediction) == test_data.shape[0]
    assert response_version == package_version

# #@pytest.mark.parametrize("api_endpoint",(("/v1/predictions/gbm"),("/v1/predictions/dl")))
# @pytest.mark.integration
# def test_shadow_mode_saves_db_gbm(flask_test_client,app, test_inputs_df):
#     # Given
#     initial_gradient_count = app.db_session.query(GradientBoostingModelPredictions).count()
#     #initial_neuralnet_count = app.db_session.query(NeuralNetModelPredictions).count()
    
#     test_data = test_inputs_df
#     post_json = test_data.to_json(orient='records') 
#     post_data = json.loads(post_json)

#     # When
#     response = flask_test_client.post("/v1/predictions/gbm", json=post_data)
#     # Then
#     assert response.status_code == 200
#     assert app.db_session.query(GradientBoostingModelPredictions).count() == initial_gradient_count + 1
#     # # The number of row increase of one because the all prediction json is put in a json field and that is in one row in the database table
#     # if api_endpoint == "/v1/predictions/gbm":
#     #     assert app.db_session.query(GradientBoostingModelPredictions).count() == initial_gradient_count + 1
#     #     print("***********")
#     #     print("Did work?")
#     #     # Because of the asynchronous input in the databse for the shadow model data prediction we have to wait but this method is not scalble. We will have to change this.

#     # else:
#     #     assert app.db_session.query(NeuralNetModelPredictions).count() == initial_neuralnet_count + 1
#     #     time.sleep(2)
#     #     assert app.db_session.query(GradientBoostingModelPredictions).count() == initial_gradient_count + 1



    