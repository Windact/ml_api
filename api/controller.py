import json
from flask import Blueprint, request, jsonify

from classification_model.predict import make_prediction
from classification_model import __version__ as _version

from api.config import get_logger
from api import __version__ as api_version
from api import validation

_logger = get_logger(logger_name=__name__)

prediction_app = Blueprint("prediction_app",__name__)

@prediction_app.route("/pumps", methods=["GET"])
def pumps():
    """ Just for quick testing purpose. Will be remove quickly """
    if request.method == "GET":
        _logger.info("pumps status is OK")
        return "Ok my dudes!"


@prediction_app.route("/version", methods=["GET"])
def version():
    if request.method == "GET":
        return jsonify({"model_verison" : _version,"api_version" : api_version})





@prediction_app.route("/v1/predict/classification", methods=["POST"])
def predict():
    if request.method == "POST":
        # Extract data from the json
        # get_json output is a str and json.loads outputs us a list(dict) that can be transformed
        # into a dataframe and that is what the predict.make_prediction function is expecting as an input.
        json_data = request.get_json()
        # print("********************************************")
        #print(json_data)
        # print("DATATYPE */*/*/*/*/*/")
        # print(f"TYPE : {type(json_data)}")
        #_logger.info(f"Inputs  : {json_data}")

        # Check if the data is valid
        input_data,errors = validation.validate_data(json_data)

        # Making the predictions
        result = make_prediction(input_data=input_data)
        _logger.info(f"Outputs : {result}")

        predictions = result.get("predictions").tolist()
        version = result.get("version")

        return jsonify({"predictions": predictions,
                        "errors" : errors,
                        "version": version})