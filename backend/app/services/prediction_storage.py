"""Persist predictions and reuse records that already exist."""

from datetime import date
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionData(TypedDict):
    """Expected structure of generated prediction data."""

    date: str
    data_source: str
    selected_model: str
    predicted_direction: int
    predicted_label: str


def save_or_get_prediction(
    db: Session,
    prediction_data: PredictionData,
) -> Prediction:
    """Save a prediction once or return its existing database record."""

    prediction_date = date.fromisoformat(prediction_data["date"])

    statement = (
        insert(Prediction)
        .values(
            prediction_date=prediction_date,
            data_source=prediction_data["data_source"],
            model_name=prediction_data["selected_model"],
            predicted_direction=prediction_data["predicted_direction"],
            predicted_label=prediction_data["predicted_label"],
        )
        .on_conflict_do_nothing(
            constraint="uq_predictions_date_source_model",
        )
    )

    try:
        db.execute(statement)

        existing_prediction = db.execute(
            select(Prediction).where(
                Prediction.prediction_date == prediction_date,
                Prediction.data_source == prediction_data["data_source"],
                Prediction.model_name == prediction_data["selected_model"],
            )
        ).scalar_one()

        db.commit()
        return existing_prediction

    except SQLAlchemyError:
        db.rollback()
        raise
