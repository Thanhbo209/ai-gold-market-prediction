"""Tests for the chronological experiment workflow."""

import numpy as np
import pandas as pd
import pytest

from gold_pipeline.experiment import run_experiment


def make_raw_data(rows: int = 240) -> pd.DataFrame:
    """Generate deterministic synthetic OHLC data."""
    rng = np.random.default_rng(42)
    returns = rng.normal(0.0005, 0.01, size=rows)
    close = 2000 * np.cumprod(1 + returns)

    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=rows, freq="D"),
            "open": close * (1 + rng.normal(0, 0.001, rows)),
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
        }
    )


def test_experiment_returns_metrics_and_chronological_counts():
    raw_data = make_raw_data()

    result = run_experiment(raw_data, train_end="2020-05-31", val_end="2020-07-31")

    assert result["row_counts"]["train"] > 0
    assert result["row_counts"]["validation"] > 0
    assert result["row_counts"]["test"] > 0

    assert result["selected_model"] in {
        "majority",
        "logistic_regression",
        "xgboost",
        "direction_persistence",
    }

    assert 0 <= result["test_classification_metrics"]["accuracy"] <= 1
    assert result["test_zero_return_metrics"]["mae"] >= 0
    assert result["xgboost_best_iteration"] >= 0

    assert (
        result["date_ranges"]["train_end"]
        < result["date_ranges"]["validation_start"]
        < result["date_ranges"]["test_start"]
    )
    if result["selected_model"] == "direction_persistence":
        assert result["selected_estimator"] is None
    else:
        assert result["selected_estimator"] is not None
        assert callable(result["selected_estimator"].predict)


def test_experiment_rejects_invalid_split_boundaries():
    with pytest.raises(ValueError, match="earlier than"):
        run_experiment(
            make_raw_data(),
            train_end="2020-08-31",
            val_end="2020-06-30",
        )
