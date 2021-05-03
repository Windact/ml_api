import pandas as pd
import pytest
import math

from classification_model import config as model_config
from classification_model import predict
from classification_model.processing import utils

from api import config

# We are marking this function so that we can set up different run time for it tests
@pytest.mark.skip
@pytest.mark.differential
def test_model_make_prediction_differential(save_file="test_data_predictions.csv"):
    """ Compare the predictions of the previous model version to the new one 
    
    Parameters
    ----------
    save_file : str, default="test_data_predictions.csv"
        The name of the file where a slice of the predictions has been saved.
    """

    # Given
    # Load the previous predictions
    previous_model_df = pd.read_csv(f"{config.PACKAGE_ROOT}/{save_file}")
    previous_model_predictions = previous_model_df["predictions"].values

    # Get the new predictions with the new model
    test_data = utils.load_dataset(filename= model_config.TESTING_DATA_FILE)
    # Taking the same slice as the capture_predictions function
    multiple_test_input = test_data.iloc[100:700,:]

    current_results = predict.make_prediction(input_data=multiple_test_input)
    current_model_predictions = current_results.get("predictions")

    # Then
    # Current model vs Previous model

    # The length
    assert len(previous_model_predictions) == len(current_model_predictions)

    # the differential test
    previous_equal_current = [previous_value == current_value for previous_value, current_value in zip(previous_model_predictions,current_model_predictions)]
    difference_rate = 1 - (sum(previous_equal_current)/len(previous_equal_current))
    # 
    assert difference_rate < model_config.ACCEPTABLE_MODEL_DIFFERENCE