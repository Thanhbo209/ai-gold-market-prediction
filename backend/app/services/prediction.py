"""Service for generating the latest gold direction prediction."""

from pathlib import Path

import pandas as pd
from gold_pipeline.prediction import predict_latest_direction

BACKEND_DIR = Path(__file__).resolve().parents[2]
PIPELINE_DIR = BACKEND_DIR / "data_pipeline"
DATA_PATH = PIPELINE_DIR / "data" / "raw" / "gc_f.csv"
ARTIFACT_DIR = PIPELINE_DIR / "artifacts" / "gc_f_experiment"


def get_latest_prediction() -> dict:
    """Load historical data and return the latest saved-model prediction."""
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Historical data not found: {DATA_PATH}")

    if not ARTIFACT_DIR.is_dir():
        raise FileNotFoundError(f"Model artifacts not found: {ARTIFACT_DIR}")

    data = pd.read_csv(DATA_PATH, parse_dates=["date"])

    return predict_latest_direction(
        data=data,
        artifact_dir=ARTIFACT_DIR,
    )
