import pytest
from pydantic import ValidationError

from app.schemas.prediction import (
    PredictionHistoryResponse,
    PredictionResponse,
)


def test_prediction_history_response_accepts_valid_data():
    prediction = PredictionResponse(
        date="2026-10-28",
        data_source="GC=F",
        selected_model="xgboost",
        predicted_direction=1,
        predicted_label="up",
    )

    response = PredictionHistoryResponse(
        items=[prediction],
        total=1,
        skip=0,
        limit=20,
    )

    assert len(response.items) == 1
    assert response.total == 1
    assert response.skip == 0
    assert response.limit == 20


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("total", -1),
        ("skip", -1),
        ("limit", 0),
    ],
)
def test_prediction_history_response_rejects_invalid_pagination(field, value):
    data = {
        "items": [],
        "total": 0,
        "skip": 0,
        "limit": 20,
    }
    data[field] = value

    with pytest.raises(ValidationError):
        PredictionHistoryResponse(**data)