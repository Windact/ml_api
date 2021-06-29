import enum
import logging
import typing as t

from sqlalchemy.orm.session import Session

from flask import current_app

from classification_model.predict import make_prediction
from dl_classification_model.predict import make_prediction as dl_make_prediction

from api.persistence.models import (
    NeuralNetModelPredictions,
    GradientBoostingModelPredictions,
)

_logger = logging.getLogger(__name__)


class ModelType(enum.Enum):
    NEURALNET = "neural net"
    GRADIENT_BOOSTING = "gradient boosting machine"


class PredictionPersistence:
    def __init__(self, *, db_session: Session, user_id: str = None) -> None:
        self.db_session = db_session
        if not user_id:
            # This app do not have an admin part so there is no actual user id. If there was we would be going for
            # current_app.user_id
            self.user_id = "gojo satoru"
    
    def make_save_predictions(self,*,input_data,db_model,app,json_data):
        """ Make the prediciton and persist it """
        with app.app_context():
            # NEURALNET
            if db_model == ModelType.NEURALNET:

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

            elif db_model == ModelType.GRADIENT_BOOSTING:
                # GBM
                # Making the predictions
                result = make_prediction(input_data=input_data)
                _logger.info(f"Outputs : {result}")

                predictions = result.get("predictions").tolist()
                version = result.get("version")

                # Save predictions
                persistence = PredictionPersistence(db_session=current_app.db_session)
                persistence.save_predictions(
                    inputs=json_data,
                    model_version=version,
                    predictions=predictions,
                    db_model=ModelType.GRADIENT_BOOSTING,
                ) 

    def save_predictions(
        self,
        *,
        inputs: t.List,
        model_version: str,
        predictions: t.List,
        db_model: ModelType,
    ) -> None:
        if db_model == ModelType.NEURALNET:
            prediction_data = NeuralNetModelPredictions(
                user_id=self.user_id,
                model_version=model_version,
                inputs=inputs,
                outputs=predictions,
            )
        elif db_model == ModelType.GRADIENT_BOOSTING:
            prediction_data = GradientBoostingModelPredictions(
                user_id=self.user_id,
                model_version=model_version,
                inputs=inputs,
                outputs=predictions,
            )

        self.db_session.add(prediction_data)
        self.db_session.commit()
        _logger.debug(f"saved data for model: {db_model}")