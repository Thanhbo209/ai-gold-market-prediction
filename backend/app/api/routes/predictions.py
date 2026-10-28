
"""Prediction API routes."""

from fastapi import APIRouter

from app.schemas.prediction import PredictionResponse
from app.services.prediction import get_latest_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/latest", response_model=PredictionResponse)
def latest_prediction() -> PredictionResponse:
    """Return the latest gold direction prediction."""
    return get_latest_prediction()
