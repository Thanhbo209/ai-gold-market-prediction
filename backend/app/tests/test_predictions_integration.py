"""Route tests for the prediction API."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.tests.test_predictions_route import (
    mock_save_or_get_prediction,
)

client = TestClient(app, raise_server_exceptions=False)

VALID_PREDICTION = {
    "date": "2026-10-27",
    "data_source": "gc_f.csv",
    "selected_model": "majority_baseline",
    "predicted_direction": 1,
    "predicted_label": "Up",
}


def test_latest_prediction_returns_valid_prediction():
    """The latest prediction endpoint returns a valid prediction."""
    with (
        patch(
            "app.api.routes.predictions.get_latest_prediction",
            return_value=VALID_PREDICTION,
        ),
        patch(
            "app.api.routes.predictions.save_or_get_prediction",
            side_effect=mock_save_or_get_prediction,
        ),
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 200
    assert response.json() == VALID_PREDICTION


def test_latest_prediction_rejects_invalid_direction():
    """An invalid prediction direction must not produce a successful response."""
    invalid_prediction = {
        **VALID_PREDICTION,
        "predicted_direction": 2,
    }

    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        return_value=invalid_prediction,
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 500
