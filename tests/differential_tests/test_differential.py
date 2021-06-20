import json
import pytest

from classification_model.config.core import config as model_config
from classification_model.processing import utils

from api import config

@pytest.mark.differential
def test_model_make_prediction_differential(flask_test_client):
    """ Compare the predictions of the previous model version to the new one """

    # Given
    test_data = utils.load_dataset(filename= model_config.app_config.TESTING_DATA_FILE)
    # Taking a slice
    test_data.iloc[100:700,:]
    post_json = test_data.to_json(orient='records') 
    post_data = json.loads(post_json)

    # When
    # Previous model
    previous_response = flask_test_client.post("/v1/predictions/dl",json=post_data)
    prev_response_json = json.loads(previous_response.data)
    prev_predictions = prev_response_json.get("predictions")
    # New model
    new_response = flask_test_client.post("/v1/predictions/gbm",json=post_data)
    new_response_json = json.loads(new_response.data)
    new_predictions = new_response_json.get("predictions")

    # The length
    assert len(prev_predictions) == len(new_predictions)

    # the differential test
    previous_equal_new = [previous_value[0] == new_value for previous_value, new_value in zip(prev_predictions,new_predictions)] # Selecting the first value of previous_value because the elements of prev_predictions list are list themself of one element.
    difference_rate = 1 - (sum(previous_equal_new)/len(previous_equal_new))
    # Checking for acceptance threshold
    print(difference_rate)
    assert difference_rate < config.ACCEPTABLE_MODEL_DIFFERENCE