"""Generate a direction prediction from historical gold OHLC data."""

from pathlib import Path
from typing import Any

import pandas as pd

from gold_pipeline.artifacts import load_model_artifact
from gold_pipeline.features import build_features


def predict_latest_direction(
    data: pd.DataFrame,
    artifact_dir: str | Path,
) -> dict[str, Any]:
    """Predict the next-observation direction using the latest valid feature row."""
    model, metadata = load_model_artifact(artifact_dir)

    features = build_features(data)

    feature_columns = metadata["feature_columns"]
    missing = set(feature_columns) - set(features.columns)
    if missing:
        raise ValueError(f"Missing model features: {', '.join(sorted(missing))}")

    latest = features.iloc[[-1]]
    x_latest = latest[feature_columns]

    prediction = int(model.predict(x_latest)[0])

    if prediction not in (0, 1):
        raise ValueError(f"Unexpected direction prediction: {prediction}")

    return {
        "date": str(latest["date"].iloc[0].date()),
        "data_source": metadata.get("data_source", "unknown"),
        "selected_model": metadata.get("selected_model", type(model).__name__),
        "predicted_direction": prediction,
        "predicted_label": "up" if prediction == 1 else "down_or_flat",
    }
