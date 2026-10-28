from datetime import date
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.prediction import Prediction
from app.services.prediction_storage import save_or_get_prediction

PREDICTION_DATA = {
    "date": "2026-10-27",
    "data_source": "GC=F",
    "selected_model": "majority",
    "predicted_direction": 1,
    "predicted_label": "up",
}


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def stored_prediction():
    return Prediction(
        prediction_date=date(2026, 10, 27),
        data_source="GC=F",
        model_name="majority",
        predicted_direction=1,
        predicted_label="up",
    )


def test_save_or_get_prediction_returns_stored_record(
    db,
    stored_prediction,
):
    result = MagicMock()
    result.scalar_one.return_value = stored_prediction
    db.execute.return_value = result

    prediction = save_or_get_prediction(db, PREDICTION_DATA)

    assert prediction is stored_prediction
    assert db.execute.call_count == 2
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_save_or_get_prediction_rolls_back_on_database_error(db):
    db.execute.side_effect = SQLAlchemyError("database failure")

    with pytest.raises(SQLAlchemyError):
        save_or_get_prediction(db, PREDICTION_DATA)

    db.rollback.assert_called_once()
    db.commit.assert_not_called()
