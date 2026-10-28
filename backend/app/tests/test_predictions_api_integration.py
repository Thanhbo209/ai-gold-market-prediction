
"""Integration tests for the predictions API."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Import the route module so its functions can be monkeypatched.
from app.api.routes import predictions as predictions_route
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.prediction import Prediction


@pytest.fixture
def api_test_db(monkeypatch):
    """Create an isolated database schema for each API integration test."""
    from os import environ

    database_url = environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("Set TEST_DATABASE_URL to your dedicated PostgreSQL test database.")

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def generated_prediction(monkeypatch):
    """Return deterministic prediction data without loading model artifacts."""
    prediction_data = {
        "date": "2026-10-27",
        "data_source": "api_test_source",
        "selected_model": "api_test_model",
        "predicted_direction": 1,
        "predicted_label": "Up",
    }

    monkeypatch.setattr(
        predictions_route,
        "get_latest_prediction",
        lambda: prediction_data,
    )
    return prediction_data


def test_latest_prediction_returns_and_persists_record(
    api_test_db,
    generated_prediction,
):
    client, session_factory = api_test_db

    response = client.get("/predictions/latest")

    assert response.status_code == 200

    body = response.json()
    assert body["date"] == generated_prediction["date"]
    assert body["data_source"] == generated_prediction["data_source"]
    assert body["selected_model"] == generated_prediction["selected_model"]
    assert body["predicted_direction"] == 1
    assert body["predicted_label"] == "Up"

    with session_factory() as db:
        count = db.scalar(
            select(func.count())
            .select_from(Prediction)
            .where(
                Prediction.prediction_date == date.fromisoformat(
                    generated_prediction["date"]
                ),
                Prediction.data_source == generated_prediction["data_source"],
                Prediction.model_name == generated_prediction["selected_model"],
            )
        )

    assert count == 1


def test_repeated_requests_do_not_create_duplicates(
    api_test_db,
    generated_prediction,
):
    client, session_factory = api_test_db

    first_response = client.get("/predictions/latest")
    second_response = client.get("/predictions/latest")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()

    with session_factory() as db:
        count = db.scalar(
            select(func.count())
            .select_from(Prediction)
            .where(
                Prediction.prediction_date == date.fromisoformat(
                    generated_prediction["date"]
                ),
                Prediction.data_source == generated_prediction["data_source"],
                Prediction.model_name == generated_prediction["selected_model"],
            )
        )

    assert count == 1


def test_missing_prediction_artifact_returns_503(
    api_test_db,
    monkeypatch,
):
    client, _ = api_test_db

    def raise_missing_file():
        raise FileNotFoundError("test model file missing")

    monkeypatch.setattr(
        predictions_route,
        "get_latest_prediction",
        raise_missing_file,
    )

    response = client.get("/predictions/latest")

    assert response.status_code == 503
    assert response.json()["detail"]


def test_invalid_prediction_output_returns_500(
    api_test_db,
    monkeypatch,
):
    client, _ = api_test_db

    def raise_invalid_prediction():
        raise ValueError("invalid model output")

    monkeypatch.setattr(
        predictions_route,
        "get_latest_prediction",
        raise_invalid_prediction,
    )

    response = client.get("/predictions/latest")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "The prediction could not be generated."
    )

def test_database_failure_returns_500(
    api_test_db,
    generated_prediction,
    monkeypatch,
):
    client, _ = api_test_db

    def raise_database_error(db, prediction_data):
        raise SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(
        predictions_route,
        "save_or_get_prediction",
        raise_database_error,
    )

    response = client.get("/predictions/latest")

    assert response.status_code == 500
    assert response.json()["detail"] == "The prediction could not be saved."
    assert "simulated database failure" not in response.text

    
def test_prediction_history_returns_empty_page(api_test_db):
    client, _ = api_test_db

    response = client.get("/predictions")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "skip": 0,
        "limit": 20,
    }


def test_prediction_history_returns_persisted_records(
    api_test_db,
    generated_prediction,
):
    client, _ = api_test_db

    # Create a record through the existing latest endpoint.
    latest_response = client.get("/predictions/latest")
    assert latest_response.status_code == 200

    response = client.get("/predictions")

    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 1
    assert body["skip"] == 0
    assert body["limit"] == 20
    assert len(body["items"]) == 1
    assert body["items"][0]["date"] == generated_prediction["date"]
    assert body["items"][0]["selected_model"] == generated_prediction["selected_model"]


@pytest.mark.parametrize(
    "query",
    [
        "?skip=-1",
        "?limit=0",
        "?limit=101",
        "?start_date=2026-10-29&end_date=2026-10-01",
    ],
)

def test_prediction_history_rejects_invalid_query_parameters(api_test_db, query):
    client, _ = api_test_db

    response = client.get(f"/predictions{query}")

    assert response.status_code == 422
