"""Database model for saved gold direction predictions."""

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prediction(Base):
    """A generated gold market direction prediction."""

    __tablename__ = "predictions"
    __table_args__ = (
        CheckConstraint(
            "predicted_direction IN (0, 1)",
            name="ck_predictions_direction",
        ),
        Index("ix_predictions_prediction_date", "prediction_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False)
    data_source: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_direction: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_label: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
