import os
from datetime import date

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.prediction import Prediction
from app.services.prediction_storage import save_or_get_prediction

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to a dedicated test database",
)


@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    try:
        with TestingSessionLocal() as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def make_prediction(model="majority"):
    return {
        "date": "2026-10-27",
        "data_source": "GC=F",
        "selected_model": model,
        "predicted_direction": 1,
        "predicted_label": "up",
    }


def test_prediction_is_inserted_into_database(db):
    prediction = save_or_get_prediction(db, make_prediction())

    assert prediction.id is not None
    assert prediction.prediction_date == date(2026, 10, 27)

    count = db.scalar(select(func.count()).select_from(Prediction))
    assert count == 1


def test_repeated_prediction_does_not_create_duplicate(db):
    first = save_or_get_prediction(db, make_prediction())
    second = save_or_get_prediction(db, make_prediction())

    assert first.id == second.id

    count = db.scalar(select(func.count()).select_from(Prediction))
    assert count == 1


def test_different_models_can_have_separate_predictions(db):
    save_or_get_prediction(db, make_prediction("majority"))
    save_or_get_prediction(db, make_prediction("xgboost"))

    count = db.scalar(select(func.count()).select_from(Prediction))
    assert count == 2
