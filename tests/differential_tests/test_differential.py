import pandas as pd
import json
import pytest

from classification_model.config.core import config as model_config
from classification_model import predict
from classification_model.processing import utils

from api import config

# We are marking this function so that we can set up different run time for it tests
#@pytest.mark.skip
# @pytest.mark.differential
# def test_model_make_prediction_differential(save_file="test_data_predictions.csv"):
#     """ Compare the predictions of the previous model version to the new one 
    
#     Parameters
#     ----------
#     save_file : str, default="test_data_predictions.csv"
#         The name of the file where a slice of the predictions has been saved.
#     """

#     # Given
#     # Load the previous predictions
#     previous_model_df = pd.read_csv(f"{config.PACKAGE_ROOT}/{save_file}")
#     previous_model_predictions = previous_model_df["predictions"].values

#     # Get the new predictions with the new model
#     test_data = utils.load_dataset(filename= model_config.app_config.TESTING_DATA_FILE)
#     # Taking the same slice as the capture_predictions function
#     multiple_test_input = test_data.iloc[100:700,:]

#     current_results = predict.make_prediction(input_data=multiple_test_input)
#     current_model_predictions = current_results.get("predictions")

#     # Then
#     # Current model vs Previous model

#     # The length
#     assert len(previous_model_predictions) == len(current_model_predictions)

#     # the differential test
#     previous_equal_current = [previous_value == current_value for previous_value, current_value in zip(previous_model_predictions,current_model_predictions)]
#     difference_rate = 1 - (sum(previous_equal_current)/len(previous_equal_current))
#     # 
#     assert difference_rate < model_config.model_config.ACCEPTABLE_MODEL_DIFFERENCE


    


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
    previous_equal_new = [previous_value == new_value for previous_value, new_value in zip(prev_predictions,new_predictions)]
    difference_rate = 1 - (sum(previous_equal_new)/len(previous_equal_new))
    # Checking for acceptance threshold
    assert difference_rate < model_config.model_config.ACCEPTABLE_MODEL_DIFFERENCE