from pathlib import Path
from typing import Any

from gold_pipeline.artifacts import save_model_artifact


def save_experiment_artifact(
    experiment_result: dict[str, Any],
    feature_columns: list[str],
    artifact_dir: str | Path,
    *,
    data_source: str = "GC=F",
) -> dict[str, Path]:
    """Save the selected experiment model and its evaluation metadata."""
    selected_model = experiment_result.get("selected_model")
    estimator = experiment_result.get("selected_estimator")

    if not selected_model:
        raise ValueError("Experiment result must include a selected model.")

    if estimator is None:
        raise ValueError(f"Cannot save '{selected_model}': no fitted estimator is available.")

    if not feature_columns:
        raise ValueError("feature_columns must not be empty.")

    required_metadata = (
        "validation_metrics",
        "test_classification_metrics",
        "test_zero_return_metrics",
        "date_ranges",
        "row_counts",
    )

    missing = [key for key in required_metadata if key not in experiment_result]
    if missing:
        raise ValueError(f"Experiment result is missing required metadata: {missing}")

    metadata = {
        "selected_model": selected_model,
        "feature_columns": feature_columns,
        "data_source": data_source,
        "validation_metrics": experiment_result["validation_metrics"],
        "test_classification_metrics": experiment_result["test_classification_metrics"],
        "test_zero_return_metrics": experiment_result["test_zero_return_metrics"],
        "date_ranges": experiment_result["date_ranges"],
        "row_counts": experiment_result["row_counts"],
        "xgboost_best_iteration": experiment_result.get("xgboost_best_iteration"),
    }

    return save_model_artifact(
        model=estimator,
        metadata=metadata,
        artifact_dir=artifact_dir,
    )
