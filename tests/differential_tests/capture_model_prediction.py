import pandas as pd

from classification_model.config.core import config as model_config
from classification_model import predict 
from classification_model.processing import utils            

from api import config

def capture_predictions():
    """ Save a slice of the predictions from the test data """

    save_file = "test_data_predictions.csv"
    test_data = utils.load_dataset(filename= model_config.app_config.TESTING_DATA_FILE)

    # Taking a slice of the test dataset
    multiple_test_input = test_data.iloc[100:700,:]

    predictions = predict.make_prediction(input_data=multiple_test_input)

    # Saving to the package root
    predictions_df = pd.DataFrame(predictions)
    predictions_df.to_csv(f"{config.PACKAGE_ROOT}/{save_file}")

if __name__ == '__main__':
    capture_predictions()