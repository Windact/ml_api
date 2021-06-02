import json
import pandas as pd 

from classification_model.processing import utils
from classification_model.config.core import config
from api import validation

def test_validate_data():
    test_data = utils.load_dataset(filename=config.app_config.TESTING_DATA_FILE)
    # Changing amount_tsh value to string when it suppose to be a float
    test_data.iloc[-1,test_data.columns.get_loc("amount_tsh")] = "This is not a float."
    post_json = test_data.to_json(orient='records')
    post_data = json.loads(post_json)

    # When
    subject_data,subject_errors = validation.validate_data(json.loads(post_json))

    # Then
    assert len(subject_errors) == 1
    input_idx =  test_data.shape[0]-1
    assert list(subject_errors.keys())[0] == input_idx
    assert list(subject_errors[input_idx].keys())[0] == "amount_tsh"



def test_prediction_endpoint_validation_200(flask_test_client):
    test_data = utils.load_dataset(filename=config.app_config.TESTING_DATA_FILE)
    post_json = test_data.to_json(orient='records') 
    post_data = json.loads(post_json)

    # When
    response = flask_test_client.post("/v1/predict/classification",json=post_data)

    # Then
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert len(response_json.get("predictions")) + len(response_json.get("errors")) == test_data.shape[0]