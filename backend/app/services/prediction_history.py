"""Database queries for historical predictions."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prediction import Prediction


def get_prediction_history(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[list[Prediction], int]:
    """Return filtered predictions, newest first, and the total match count."""
    filters = []

    if start_date is not None:
        filters.append(Prediction.prediction_date >= start_date)

    if end_date is not None:
        filters.append(Prediction.prediction_date <= end_date)

    count_statement = select(func.count()).select_from(Prediction)
    records_statement = select(Prediction)

    if filters:
        count_statement = count_statement.where(*filters)
        records_statement = records_statement.where(*filters)

    total = db.scalar(count_statement) or 0

    records_statement = (
        records_statement.order_by(Prediction.prediction_date.desc(), Prediction.id.desc())
        .offset(skip)
        .limit(limit)
    )

    records = list(db.scalars(records_statement).all())

    return records, total
