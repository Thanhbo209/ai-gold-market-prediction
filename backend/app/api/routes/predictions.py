"""Prediction API routes."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.prediction import PredictionResponse
from app.services.prediction import get_latest_prediction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/latest", response_model=PredictionResponse)
def latest_prediction() -> PredictionResponse:
    """Return the latest gold direction prediction."""
    try:
        return get_latest_prediction()

    except FileNotFoundError as exc:
        logger.warning("Prediction unavailable because a required file is missing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction is temporarily unavailable because required data or model "
            "artifactsare missing.",
        ) from exc

    except ValueError as exc:
        logger.exception("Prediction generation failed because of invalid data or model output")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction could not be generated.",
        ) from exc
