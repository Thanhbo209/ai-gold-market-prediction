"""Simple baselines for daily gold-price prediction."""

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gold_pipeline.features import FEATURE_COLUMNS


def predict_zero_return(index: pd.Index) -> pd.Series:
    """Predict zero return for every observation."""
    return pd.Series(0.0, index=index, name="predicted_return")


def predict_persistent_direction(features: pd.DataFrame) -> pd.Series:
    """Predict the next direction from the current day's return direction."""
    if "return_1" not in features.columns:
        raise ValueError("Features must contain return_1.")

    predictions = (features["return_1"] > 0).astype("int8")
    predictions.name = "predicted_direction"
    return predictions


def fit_majority_classifier(
    train_features: pd.DataFrame,
    train_directions: pd.Series,
) -> DummyClassifier:
    """Fit a classifier that always predicts the training majority class."""
    if train_features.empty or train_directions.empty:
        raise ValueError("Training data cannot be empty.")

    if len(train_features) != len(train_directions):
        raise ValueError("Features and labels must have the same length.")

    model = DummyClassifier(strategy="most_frequent")
    model.fit(train_features[FEATURE_COLUMNS], train_directions)
    return model


def fit_logistic_classifier(
    train_features: pd.DataFrame,
    train_directions: pd.Series,
) -> object:
    """Fit a simple standardized logistic regression direction classifier."""
    if train_features.empty or train_directions.empty:
        raise ValueError("Training data cannot be empty.")

    if len(train_features) != len(train_directions):
        raise ValueError("Features and labels must have the same length.")

    if train_directions.nunique() < 2:
        raise ValueError("Training labels must contain both direction classes.")

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1_000, random_state=42),
    )
    model.fit(train_features[FEATURE_COLUMNS], train_directions)
    return model
