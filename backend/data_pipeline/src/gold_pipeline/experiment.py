"""Run a chronological gold-direction prediction experiment."""

import pandas as pd

from gold_pipeline.baselines import (
    fit_logistic_classifier,
    fit_majority_classifier,
    predict_persistent_direction,
)
from gold_pipeline.features import FEATURE_COLUMNS, build_features
from gold_pipeline.labels import build_labels
from gold_pipeline.metrics import classification_metrics, regression_metrics
from gold_pipeline.splits import chronological_split
from gold_pipeline.xgboost_model import fit_xgboost_classifier


def run_experiment(
    raw_data: pd.DataFrame,
    *,
    train_end: str,
    val_end: str,
    gap: int = 1,
) -> dict:
    """Compare classifiers on validation data and evaluate the winner on test."""
    features = build_features(raw_data)
    labels = build_labels(raw_data)

    dataset = features.merge(
        labels,
        on="date",
        how="inner",
        validate="one_to_one",
    )

    if dataset.empty:
        raise ValueError("No rows remain after joining features and labels.")

    train, validation, test = chronological_split(
        dataset,
        train_end=train_end,
        val_end=val_end,
        gap=gap,
    )

    def get_features(frame: pd.DataFrame) -> pd.DataFrame:
        return frame[FEATURE_COLUMNS]

    x_train = get_features(train)
    x_val = get_features(validation)
    x_test = get_features(test)

    y_train = train["target_direction"]
    y_val = validation["target_direction"]
    y_test = test["target_direction"]

    # Fit all candidates on training data only.
    majority_model = fit_majority_classifier(x_train, y_train)
    logistic_model = fit_logistic_classifier(x_train, y_train)
    xgboost_model = fit_xgboost_classifier(
        x_train,
        y_train,
        x_val,
        y_val,
    )

    validation_predictions = {
        "majority": majority_model.predict(x_val),
        "logistic_regression": logistic_model.predict(x_val),
        "xgboost": xgboost_model.predict(x_val),
        "direction_persistence": predict_persistent_direction(validation[["return_1"]]).to_numpy(),
    }

    validation_metrics = {
        name: classification_metrics(y_val, predictions)
        for name, predictions in validation_predictions.items()
    }

    # Select by validation accuracy only; never use test metrics for selection.
    selected_name = max(
        validation_metrics,
        key=lambda name: validation_metrics[name]["accuracy"],
    )

    selected_models = {
        "majority": majority_model,
        "logistic_regression": logistic_model,
        "xgboost": xgboost_model,
    }

    if selected_name == "direction_persistence":
        test_predictions = predict_persistent_direction(test[["return_1"]]).to_numpy()
    else:
        test_predictions = selected_models[selected_name].predict(x_test)

    test_classification_metrics = classification_metrics(
        y_test,
        test_predictions,
    )

    # A simple return-prediction baseline: predict zero return.
    zero_return_predictions = pd.Series(0.0, index=test.index)
    test_return_metrics = regression_metrics(
        test["target_return"],
        zero_return_predictions,
    )

    selected_estimator = selected_models.get(selected_name)

    return {
        "row_counts": {
            "train": len(train),
            "validation": len(validation),
            "test": len(test),
        },
        "validation_metrics": validation_metrics,
        "selected_model": selected_name,
        "selected_estimator": selected_estimator,
        "test_classification_metrics": test_classification_metrics,
        "test_zero_return_metrics": test_return_metrics,
        "xgboost_best_iteration": int(xgboost_model.best_iteration),
        "date_ranges": {
            "train_start": str(train["date"].min().date()),
            "train_end": str(train["date"].max().date()),
            "validation_start": str(validation["date"].min().date()),
            "validation_end": str(validation["date"].max().date()),
            "test_start": str(test["date"].min().date()),
            "test_end": str(test["date"].max().date()),
        },
    }
