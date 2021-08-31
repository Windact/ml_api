import logging
from flask import request, jsonify, Response,current_app
# Threading is better here than multiprocessing because start another process will make the user
# wait too much.
# Nevertheless, the way we implement it is not scalable. We will change it latter.
import threading

from classification_model.predict import make_prediction
from classification_model import __version__ as _version
from dl_classification_model.predict import make_prediction as dl_make_prediction
from dl_classification_model import __version__ as shadow_version

from flask import current_app

from prometheus_client import Counter, Info

from api.config import get_logger
from api import __version__ as api_version
from api import validation
from api.persistence.data_access import PredictionPersistence, ModelType
from api.config import APP_NAME


#from api.monitoring.middleware import PREDICTION_Counter_FAULTY_WATER_PUMPS,PREDICTION_Counter_HEALTHY_WATER_PUMPS
_logger = logging.getLogger('mlapi')

# GRADIENT_BOOSTING should be the shadow model as it the new and improve one but whatever

PREDICTION_Counter_FAULTY_WATER_PUMPS = Counter(
    name='faulty_waterpumps_counter',
    documentation='Faulty waterpumps counter',
    labelnames=['app_name', 'model_name', 'model_version']
)

PREDICTION_Counter_HEALTHY_WATER_PUMPS = Counter(
    name='healthy_waterpumps_counter',
    documentation='Healthy waterpumps counter',
    labelnames=['app_name', 'model_name', 'model_version']
)

# PREDICTION_Counter_FAULTY_WATER_PUMPS.labels(
#                 app_name=APP_NAME,
#                 model_name=ModelType.GRADIENT_BOOSTING.name,
#                 model_version=_version)

# PREDICTION_Counter_HEALTHY_WATER_PUMPS.labels(
#                 app_name=APP_NAME,
#                 model_name=ModelType.GRADIENT_BOOSTING.name,
#                 model_version=_version)

MODEL_VERSIONS = Info(
    'model_version_details',
    'Capture model version information',
)

# That information will be tracked now. i do not need to add it to and endpoint.
MODEL_VERSIONS.info({
    'live_model': ModelType.GRADIENT_BOOSTING.name,
    'live_version': _version,
    'shadow_model': ModelType.NEURALNET.name,
    'shadow_version': shadow_version})

def pumps():
    """ Just for quick testing purpose. Will be remove quickly """
    if request.method == "GET":
        _logger.info("pumps status is OK")
        return jsonify({"Status":"Ok"})


def version():
    if request.method == "GET":
        _logger.debug(f"model_verison {_version}, api_version : {api_version}")
        return jsonify({"model_verison" : _version,"api_version" : api_version})


def predict():
    if request.method == "POST":
        # Extract data from the json
        # get_json output is a str and json.loads outputs us a list(dict) that can be transformed
        # into a dataframe and that is what the predict.make_prediction function is expecting as an input.
        # NOT REALLY ANYMORE
        json_data = request.get_json()
        _logger.info(f"Inputs  : {json_data}"
                    f"model : {ModelType.GRADIENT_BOOSTING.name}"
                    f"model_version : {_version}"
                    )

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

        # Monitoring
        for pred in predictions:
            if pred == "functional":
                PREDICTION_Counter_HEALTHY_WATER_PUMPS.labels(
                app_name=APP_NAME,
                model_name=ModelType.GRADIENT_BOOSTING.name,
                model_version=_version).inc()
            elif pred == "non functional or functional needs repair":
                PREDICTION_Counter_FAULTY_WATER_PUMPS.labels(
                app_name=APP_NAME,
                model_name=ModelType.GRADIENT_BOOSTING.name,
                model_version=_version).inc()

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
        _logger.info(f"Inputs  : {json_data}"
                    f"model : {ModelType.NEURALNET.name}"
                    f"model_version : {shadow_version}"
                    )

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


