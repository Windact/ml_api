import json
import pytest

from classification_model.processing import utils
from classification_model.config.core import config
from api import validation


@pytest.mark.parametrize("var_name,var_index,var_value",[("amount_tsh",-1,"This is not a float."),("construction_year",-5,"Not int"),("public_meeting",-3,45)])
def test_validate_data(var_name,var_index,var_value):
    test_data = utils.load_dataset(filename=config.app_config.TESTING_DATA_FILE)
    # Changing amount_tsh value to string when it suppose to be a float
    test_data.iloc[var_index,test_data.columns.get_loc(var_name)] = var_value
    post_json = test_data.to_json(orient='records')

    # When
    _,subject_errors = validation.validate_data(json.loads(post_json))

    # Then
    assert len(subject_errors) == 1
    input_idx =  test_data.shape[0]+var_index
    assert list(subject_errors.keys())[0] == input_idx
    assert list(subject_errors[input_idx].keys())[0] == var_name


@pytest.mark.integration
def test_prediction_endpoint_validation_200(flask_test_client):
    test_data = utils.load_dataset(filename=config.app_config.TESTING_DATA_FILE)
    post_json = test_data.to_json(orient='records') 
    post_data = json.loads(post_json)

    # When
    response = flask_test_client.post("/v1/predictions",json=post_data)

    # Then
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert len(response_json.get("predictions")) + len(response_json.get("errors")) == test_data.shape[0]



