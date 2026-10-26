"""Tests for the XGBoost direction classifier."""

import numpy as np
import pandas as pd
import pytest

from gold_pipeline.features import FEATURE_COLUMNS
from gold_pipeline.xgboost_model import fit_xgboost_classifier


def make_features(rows: int, seed: int) -> pd.DataFrame:
    """Create deterministic synthetic features for model tests."""
    rng = np.random.default_rng(seed)

    return pd.DataFrame(
        rng.normal(size=(rows, len(FEATURE_COLUMNS))),
        columns=FEATURE_COLUMNS,
    )


def make_labels(features: pd.DataFrame) -> pd.Series:
    """Create binary labels related to the first feature."""
    return (features["return_1"] > 0).astype("int8")


def test_xgboost_fits_and_predicts_binary_directions():
    train_features = make_features(120, seed=1)
    val_features = make_features(40, seed=2)

    train_labels = make_labels(train_features)
    val_labels = make_labels(val_features)

    model = fit_xgboost_classifier(
        train_features,
        train_labels,
        val_features,
        val_labels,
        n_estimators=30,
        early_stopping_rounds=5,
    )

    predictions = model.predict(val_features)

    assert len(predictions) == len(val_features)
    assert set(predictions).issubset({0, 1})
    assert model.best_iteration >= 0
    assert "validation_0" in model.evals_result()


def test_xgboost_rejects_mismatched_training_lengths():
    train_features = make_features(10, seed=1)
    val_features = make_features(10, seed=2)

    with pytest.raises(ValueError, match="same length"):
        fit_xgboost_classifier(
            train_features,
            pd.Series([0, 1] * 4),
            val_features,
            make_labels(val_features),
            n_estimators=10,
            early_stopping_rounds=3,
        )


def test_xgboost_rejects_single_class_training_labels():
    train_features = make_features(20, seed=1)
    val_features = make_features(10, seed=2)

    with pytest.raises(ValueError, match="both direction classes"):
        fit_xgboost_classifier(
            train_features,
            pd.Series([1] * len(train_features)),
            val_features,
            make_labels(val_features),
            n_estimators=10,
            early_stopping_rounds=3,
        )


def test_xgboost_rejects_missing_feature_columns():
    train_features = make_features(20, seed=1).drop(columns=["return_1"])
    val_features = make_features(10, seed=2)

    with pytest.raises(ValueError, match="missing columns"):
        fit_xgboost_classifier(
            train_features,
            pd.Series([0, 1] * 10),
            val_features,
            make_labels(val_features),
            n_estimators=10,
            early_stopping_rounds=3,
        )


def test_xgboost_shuffled_labels_do_not_produce_strong_validation_accuracy():
    """Shuffled training labels should destroy the learnable signal."""
    rng = np.random.default_rng(123)

    train_features = make_features(500, seed=10)
    val_features = make_features(200, seed=11)

    # The true target is related to return_1.
    train_labels = make_labels(train_features)
    val_labels = make_labels(val_features)

    # Break the relationship between training features and training labels.
    shuffled_train_labels = pd.Series(
        rng.permutation(train_labels.to_numpy()),
        index=train_labels.index,
    )

    model = fit_xgboost_classifier(
        train_features,
        shuffled_train_labels,
        val_features,
        val_labels,
        n_estimators=80,
        early_stopping_rounds=10,
        random_state=42,
    )

    predictions = model.predict(val_features)
    accuracy = (predictions == val_labels.to_numpy()).mean()

    # A deliberately loose threshold allows random variation while
    # detecting a suspiciously strong result from shuffled labels.
    assert accuracy < 0.70
