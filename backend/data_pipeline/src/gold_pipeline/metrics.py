"""Evaluation metrics for gold-price prediction."""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error


def regression_metrics(
    actual_returns: pd.Series,
    predicted_returns: pd.Series,
) -> dict[str, float]:
    """Evaluate next-observation return predictions."""
    actual = np.asarray(actual_returns, dtype=float)
    predicted = np.asarray(predicted_returns, dtype=float)

    if actual.size == 0:
        raise ValueError("Cannot evaluate empty predictions.")

    if actual.shape != predicted.shape:
        raise ValueError("Actual and predicted values must have the same shape.")

    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Actual and predicted values must be finite.")

    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "directional_accuracy": float(accuracy_score(actual > 0, predicted > 0)),
    }


def classification_metrics(
    actual_directions: pd.Series,
    predicted_directions: pd.Series,
) -> dict[str, float]:
    """Evaluate binary direction predictions."""
    actual = np.asarray(actual_directions)
    predicted = np.asarray(predicted_directions)

    if actual.size == 0:
        raise ValueError("Cannot evaluate empty predictions.")

    if actual.shape != predicted.shape:
        raise ValueError("Actual and predicted values must have the same shape.")

    if not np.isin(actual, [0, 1]).all():
        raise ValueError("Actual directions must contain only 0 and 1.")

    if not np.isin(predicted, [0, 1]).all():
        raise ValueError("Predicted directions must contain only 0 and 1.")

    return {
        "accuracy": float(accuracy_score(actual, predicted)),
    }
