
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PREDICTION = {
    "date": "2026-10-27",
    "data_source": "GC=F",
    "selected_model": "majority",
    "predicted_direction": 1,
    "predicted_label": "up",
}


def test_get_latest_prediction_returns_prediction():
    from unittest.mock import patch

    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        return_value=PREDICTION,
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 200
    assert response.json() == PREDICTION


def test_get_latest_prediction_validates_response():
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    invalid_prediction = {
        **PREDICTION,
        "predicted_direction": 2,
    }

    test_client = TestClient(app, raise_server_exceptions=False)
    
    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        return_value=invalid_prediction,
    ):
        response = test_client.get("/predictions/latest")

    assert response.status_code == 500
