
"""Integration tests for prediction history queries."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.prediction import Prediction
from app.services.prediction_history import get_prediction_history


@pytest.fixture
def db():
    """Provide a clean database session for each test."""
    import os

    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("Set TEST_DATABASE_URL to your dedicated test database.")

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def add_prediction(
    db: Session,
    prediction_date: date,
    model_name: str = "majority",
) -> Prediction:
    """Insert a prediction for history-query tests."""
    prediction = Prediction(
        prediction_date=prediction_date,
        data_source="history_test_source",
        model_name=model_name,
        predicted_direction=1,
        predicted_label="up",
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def test_empty_history_returns_no_records_and_zero_total(db):
    records, total = get_prediction_history(db)

    assert records == []
    assert total == 0


def test_history_returns_newest_first(db):
    add_prediction(db, date(2026, 10, 20))
    add_prediction(db, date(2026, 10, 25))

    records, total = get_prediction_history(db)

    assert total == 2
    assert [record.prediction_date for record in records] == [
        date(2026, 10, 25),
        date(2026, 10, 20),
    ]


def test_history_applies_pagination(db):
    for day in (20, 21, 22):
        add_prediction(db, date(2026, 10, day))

    records, total = get_prediction_history(db, skip=1, limit=1)

    assert total == 3
    assert len(records) == 1
    assert records[0].prediction_date == date(2026, 10, 21)


def test_history_filters_dates_inclusively(db):
    for day in (20, 21, 22, 23):
        add_prediction(db, date(2026, 10, day))

    records, total = get_prediction_history(
        db,
        start_date=date(2026, 10, 21),
        end_date=date(2026, 10, 22),
    )

    assert total == 2
    assert [record.prediction_date for record in records] == [
        date(2026, 10, 22),
        date(2026, 10, 21),
    ]


def test_total_counts_all_matching_records_not_only_current_page(db):
    for day in (20, 21, 22):
        add_prediction(db, date(2026, 10, day))

    records, total = get_prediction_history(db, limit=1)

    assert len(records) == 1
    assert total == 3
