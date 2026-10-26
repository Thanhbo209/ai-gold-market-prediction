"""Tests for prediction evaluation metrics."""

import pandas as pd
import pytest

from gold_pipeline.metrics import (
    classification_metrics,
    regression_metrics,
)


def test_regression_metrics_calculate_expected_values():
    actual = pd.Series([0.1, -0.1, 0.2])
    predicted = pd.Series([0.0, -0.2, 0.1])

    result = regression_metrics(actual, predicted)

    assert result["mae"] == pytest.approx(0.1)
    assert result["rmse"] == pytest.approx((0.03 / 3) ** 0.5)
    assert result["directional_accuracy"] == pytest.approx(2 / 3)


def test_regression_metrics_reject_empty_input():
    with pytest.raises(ValueError, match="empty"):
        regression_metrics(pd.Series(dtype=float), pd.Series(dtype=float))


def test_regression_metrics_reject_different_lengths():
    with pytest.raises(ValueError, match="same shape"):
        regression_metrics(pd.Series([0.1]), pd.Series([0.1, 0.2]))


def test_regression_metrics_reject_nan():
    with pytest.raises(ValueError, match="finite"):
        regression_metrics(pd.Series([float("nan")]), pd.Series([0.0]))


def test_classification_metrics_calculate_accuracy():
    actual = pd.Series([1, 0, 1, 1])
    predicted = pd.Series([1, 0, 0, 1])

    result = classification_metrics(actual, predicted)

    assert result["accuracy"] == pytest.approx(0.75)


def test_classification_metrics_reject_invalid_labels():
    with pytest.raises(ValueError, match="only 0 and 1"):
        classification_metrics(pd.Series([0, 2]), pd.Series([0, 1]))


def test_classification_metrics_reject_different_lengths():
    with pytest.raises(ValueError, match="same shape"):
        classification_metrics(pd.Series([1]), pd.Series([1, 0]))
