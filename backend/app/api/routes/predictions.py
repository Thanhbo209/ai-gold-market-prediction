"""Prediction API routes."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prediction import (
    PredictionHistoryResponse,
    PredictionResponse,
)
from app.services.prediction import get_latest_prediction
from app.services.prediction_history import get_prediction_history
from app.services.prediction_storage import save_or_get_prediction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/latest", response_model=PredictionResponse)
def latest_prediction(
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Return the latest gold direction prediction."""

    # Generate the prediction.
    try:
        prediction_data = get_latest_prediction()

    except FileNotFoundError as exc:
        logger.warning(
            "Prediction unavailable because a required file is missing: %s",
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Prediction is temporarily unavailable because required "
                "data or model artifacts are missing."
            ),
        ) from exc

    except ValueError as exc:
        logger.exception("Prediction generation failed due to invalid data or model output")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction could not be generated.",
        ) from exc

    # Persist the prediction or retrieve the existing record.
    try:
        stored = save_or_get_prediction(db, prediction_data)

    except (ValueError, KeyError) as exc:
        logger.exception("Prediction persistence failed due to invalid prediction data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction data could not be saved.",
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception("Database operation failed while saving the prediction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction could not be saved.",
        ) from exc

    # Return the persisted database record.
    return PredictionResponse(
        date=stored.prediction_date.isoformat(),
        data_source=stored.data_source,
        selected_model=stored.model_name,
        predicted_direction=stored.predicted_direction,
        predicted_label=stored.predicted_label,
    )


@router.get("", response_model=PredictionHistoryResponse)
def prediction_history(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: date | None = None,
    end_date: date | None = None,
) -> PredictionHistoryResponse:
    """Return stored prediction history with pagination and date filters."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_date must be on or before end_date.",
        )

    try:
        records, total = get_prediction_history(
            db,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
    except SQLAlchemyError as exc:
        logger.exception("Database operation failed while retrieving prediction history")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction history could not be retrieved.",
        ) from exc

    items = [
        PredictionResponse(
            date=record.prediction_date.isoformat(),
            data_source=record.data_source,
            selected_model=record.model_name,
            predicted_direction=record.predicted_direction,
            predicted_label=record.predicted_label,
        )
        for record in records
    ]

    return PredictionHistoryResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
