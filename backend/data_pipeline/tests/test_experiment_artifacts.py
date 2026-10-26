import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from gold_pipeline.artifacts import load_model_artifact
from gold_pipeline.experiment_artifacts import save_experiment_artifact


@pytest.fixture
def fitted_model_and_features():
    features = pd.DataFrame(
        {
            "return_1": [0.01, -0.02, 0.03, -0.01],
            "volatility_5": [0.1, 0.2, 0.15, 0.12],
        }
    )
    target = [1, 0, 1, 0]

    model = DummyClassifier(strategy="most_frequent")
    model.fit(features, target)

    return model, features


@pytest.fixture
def experiment_result(fitted_model_and_features):
    model, _ = fitted_model_and_features

    return {
        "selected_model": "logistic_regression",
        "selected_estimator": model,
        "validation_metrics": {
            "accuracy": 0.65,
            "balanced_accuracy": 0.60,
        },
        "test_classification_metrics": {
            "accuracy": 0.70,
        },
        "test_zero_return_metrics": {
            "accuracy": 0.72,
        },
        "date_ranges": {
            "train_start": "2020-01-01",
            "train_end": "2020-05-31",
            "validation_start": "2020-06-01",
            "validation_end": "2020-07-31",
            "test_start": "2020-08-01",
            "test_end": "2020-09-30",
        },
        "row_counts": {
            "train": 100,
            "validation": 40,
            "test": 40,
        },
        "xgboost_best_iteration": 12,
    }


def test_saves_selected_model_and_experiment_metadata(
    tmp_path,
    experiment_result,
):
    artifact_dir = tmp_path / "model"
    feature_columns = ["return_1", "volatility_5"]

    saved_path = save_experiment_artifact(
        experiment_result,
        feature_columns,
        artifact_dir,
    )

    assert saved_path["model_path"] == artifact_dir / "model.joblib"
    assert saved_path["metadata_path"] == artifact_dir / "metadata.json"

    loaded_model, metadata = load_model_artifact(artifact_dir)

    assert metadata["selected_model"] == "logistic_regression"
    assert metadata["feature_columns"] == feature_columns
    assert metadata["data_source"] == "GC=F"
    assert metadata["validation_metrics"] == experiment_result["validation_metrics"]
    assert (
        metadata["test_classification_metrics"] == experiment_result["test_classification_metrics"]
    )
    assert metadata["test_zero_return_metrics"] == experiment_result["test_zero_return_metrics"]
    assert metadata["date_ranges"] == experiment_result["date_ranges"]
    assert metadata["row_counts"] == experiment_result["row_counts"]
    assert metadata["xgboost_best_iteration"] == experiment_result["xgboost_best_iteration"]


def test_saved_model_reproduces_predictions(
    tmp_path,
    fitted_model_and_features,
    experiment_result,
):
    original_model, features = fitted_model_and_features

    save_experiment_artifact(
        experiment_result,
        list(features.columns),
        tmp_path / "model",
    )

    loaded_model, _ = load_model_artifact(tmp_path / "model")

    original_predictions = original_model.predict(features)
    loaded_predictions = loaded_model.predict(features)

    np.testing.assert_array_equal(
        loaded_predictions,
        original_predictions,
    )


def test_rejects_missing_selected_model(tmp_path):
    with pytest.raises(ValueError, match="selected model"):
        save_experiment_artifact(
            {"selected_estimator": DummyClassifier()},
            ["return_1"],
            tmp_path / "model",
        )


def test_rejects_missing_estimator_for_persistence_baseline(
    tmp_path,
):
    result = {
        "selected_model": "direction_persistence",
        "selected_estimator": None,
    }

    with pytest.raises(ValueError, match="no fitted estimator"):
        save_experiment_artifact(
            result,
            ["return_1"],
            tmp_path / "model",
        )


def test_rejects_missing_experiment_metadata(
    tmp_path,
    experiment_result,
):
    incomplete_result = {
        "selected_model": experiment_result["selected_model"],
        "selected_estimator": experiment_result["selected_estimator"],
    }

    with pytest.raises(ValueError, match="missing required metadata"):
        save_experiment_artifact(
            incomplete_result,
            ["return_1"],
            tmp_path / "model",
        )


def test_rejects_empty_feature_columns(
    tmp_path,
    experiment_result,
):
    with pytest.raises(ValueError, match="feature_columns"):
        save_experiment_artifact(
            experiment_result,
            [],
            tmp_path / "model",
        )


def test_rejects_non_json_serializable_metadata(
    tmp_path,
    experiment_result,
):
    experiment_result["validation_metrics"] = {
        "accuracy": object(),
    }

    with pytest.raises((TypeError, ValueError)):
        save_experiment_artifact(
            experiment_result,
            ["return_1", "volatility_5"],
            tmp_path / "model",
        )

    assert not (tmp_path / "model" / "metadata.json").exists()
