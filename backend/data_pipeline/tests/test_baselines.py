"""Tests for baseline prediction models."""

import pandas as pd
import pytest

from gold_pipeline.baselines import (
    fit_logistic_classifier,
    fit_majority_classifier,
    predict_persistent_direction,
    predict_zero_return,
)
from gold_pipeline.features import FEATURE_COLUMNS


def make_features(rows: int = 20) -> pd.DataFrame:
    """Create deterministic features for baseline tests."""
    data = {column: [float(index + 1) for index in range(rows)] for column in FEATURE_COLUMNS}
    data["return_1"] = [-0.01 if index % 2 == 0 else 0.01 for index in range(rows)]
    return pd.DataFrame(data)


def test_zero_return_predicts_zero_for_every_row():
    index = pd.Index([10, 11, 12])

    predictions = predict_zero_return(index)

    assert predictions.tolist() == [0.0, 0.0, 0.0]
    assert predictions.index.equals(index)


def test_persistent_direction_uses_current_return_sign():
    features = pd.DataFrame({"return_1": [-0.1, 0.0, 0.2]})

    predictions = predict_persistent_direction(features)

    assert predictions.tolist() == [0, 0, 1]


def test_persistent_direction_requires_return_feature():
    with pytest.raises(ValueError, match="return_1"):
        predict_persistent_direction(pd.DataFrame({"return_5": [0.1]}))


def test_majority_classifier_learns_from_training_labels():
    features = make_features()
    labels = pd.Series([1, 1, 0, 1, 0] * 4)

    model = fit_majority_classifier(features, labels)
    predictions = model.predict(features[FEATURE_COLUMNS])

    assert set(predictions) == {1}


def test_logistic_classifier_fits_and_predicts_binary_directions():
    features = make_features()
    labels = pd.Series([0, 1] * 10)

    model = fit_logistic_classifier(features, labels)
    predictions = model.predict(features[FEATURE_COLUMNS])

    assert len(predictions) == len(labels)
    assert set(predictions).issubset({0, 1})


def test_logistic_classifier_rejects_single_class_training_data():
    features = make_features()
    labels = pd.Series([1] * len(features))

    with pytest.raises(ValueError, match="both direction classes"):
        fit_logistic_classifier(features, labels)
