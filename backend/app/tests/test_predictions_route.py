from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


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


def test_missing_prediction_file_returns_503():
    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        side_effect=FileNotFoundError("private/path/gc_f.csv"),
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Prediction is temporarily unavailable because required data or model artifacts" \
        "are missing."

    }
    assert "private/path" not in response.text


def test_prediction_value_error_returns_500():
    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        side_effect=ValueError("Unexpected direction prediction: 2"),
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 500
    assert response.json() == {"detail": "The prediction could not be generated."}
    assert "Unexpected direction prediction" not in response.text


def test_unexpected_error_returns_generic_500():
    with patch(
        "app.api.routes.predictions.get_latest_prediction",
        side_effect=RuntimeError("internal implementation detail"),
    ):
        response = client.get("/predictions/latest")

    assert response.status_code == 500
    assert "internal implementation detail" not in response.text
