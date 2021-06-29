from flask import request, jsonify, Response,current_app
# Threading is better here than multiprocessing because start another process will make the user
# wait too much.
# Nevertheless, the way we implement it is not scalable. We will change it latter.
import threading

from classification_model.predict import make_prediction
from classification_model import __version__ as _version
from dl_classification_model.predict import make_prediction as dl_make_prediction

from flask import current_app

from api.config import get_logger
from api import __version__ as api_version
from api import validation
from api.persistence.data_access import PredictionPersistence, ModelType

_logger = get_logger(logger_name=__name__)

def pumps():
    """ Just for quick testing purpose. Will be remove quickly """
    if request.method == "GET":
        _logger.info("pumps status is OK")
        return jsonify({"Status":"Ok"})


def version():
    if request.method == "GET":
        return jsonify({"model_verison" : _version,"api_version" : api_version})


def predict():
    if request.method == "POST":
        # Extract data from the json
        # get_json output is a str and json.loads outputs us a list(dict) that can be transformed
        # into a dataframe and that is what the predict.make_prediction function is expecting as an input.
        # NOT REALLY ANYMORE
        json_data = request.get_json()
        _logger.info(f"Inputs  : {json_data}")

        # Check if the data is valid
        input_data,errors = validation.validate_data(json_data)

        # Making the predictions
        result = make_prediction(input_data=input_data)
        _logger.info(f"Outputs : {result}")

        predictions = result.get("predictions").tolist()

        version = result.get("version")

        # Persisting the predictions
        persistence = PredictionPersistence(db_session=current_app.db_session)

        persistence.save_predictions(
            inputs=json_data,
            model_version=version,
            predictions=predictions,
            db_model=ModelType.GRADIENT_BOOSTING,
        )

        # Asynchronous shadow mode
        if current_app.config.get("SHADOW_MODE_ACTIVE"):
            _logger.debug(
                f"Calling shadow model asynchronously: "
                f"{ModelType.NEURALNET.value}"
            )
            thread = threading.Thread(
                target=persistence.make_save_predictions,
                kwargs={
                    "db_model": ModelType.NEURALNET,
                    "input_data": input_data,
                    "app": current_app._get_current_object(),
                    "json_data": json_data
                },
            )
            thread.start()

        return jsonify({"predictions": predictions,
                        "errors" : errors,
                        "version": version})



def prev_predict():
    if request.method == "POST":
        # Extract data from the json
        # get_json output is a str and json.loads outputs us a list(dict) that can be transformed
        # into a dataframe and that is what the predict.make_prediction function is expecting as an input.
        # NOT REALLY ANYMORE
        json_data = request.get_json()
        _logger.info(f"Inputs  : {json_data}")

        # Check if the data is valid
        input_data,errors = validation.validate_data(json_data)

        # Making the predictions
        result = dl_make_prediction(input_data=input_data)
        _logger.info(f"Outputs : {result}")

        predictions = result.get("predictions").tolist()
        version = result.get("version")

        # Save predictions
        persistence = PredictionPersistence(db_session=current_app.db_session)

        persistence.save_predictions(
            inputs=json_data,
            model_version=version,
            predictions=predictions,
            db_model=ModelType.NEURALNET,
        )

        # Asynchronous shadow mode
        if current_app.config.get("SHADOW_MODE_ACTIVE"):
            _logger.debug(
                f"Calling shadow model asynchronously: "
                f"{ModelType.GRADIENT_BOOSTING.value}"
            )
            thread = threading.Thread(
                target=persistence.make_save_predictions,
                kwargs={
                    "db_model": ModelType.GRADIENT_BOOSTING,
                    "input_data": input_data,
                    "app": current_app._get_current_object(),
                    "json_data": json_data
                },
            )
            thread.start()

        return jsonify({"predictions": predictions,
                        "errors" : errors,
                        "version": version})


