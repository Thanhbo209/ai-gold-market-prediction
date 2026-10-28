"""Integration tests for the prediction API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_PREDICTION = {
    "date": "2026-10-27",
    "data_source": "gc_f.csv",
    "selected_model": "majority_baseline",
    "predicted_direction": 1,
    "predicted_label": "Up",
}


def test_latest_prediction_returns_valid_prediction(monkeypatch):
    """The latest prediction endpoint returns a valid prediction."""

    def mock_get_latest_prediction():
        return VALID_PREDICTION

    monkeypatch.setattr(
        "app.api.routes.predictions.get_latest_prediction",
        mock_get_latest_prediction,
    )

    response = client.get("/predictions/latest")

    assert response.status_code == 200
    assert response.json() == VALID_PREDICTION


def test_latest_prediction_rejects_invalid_direction(monkeypatch):
    """An invalid prediction direction must not produce a successful response."""
    invalid_prediction = {
        **VALID_PREDICTION,
        "predicted_direction": 2,
    }

    monkeypatch.setattr(
        "app.api.routes.predictions.get_latest_prediction",
        lambda: invalid_prediction,
    )

    response = client.get("/predictions/latest")

    assert response.status_code == 500
