"""Run a gold-direction experiment from a historical CSV file."""

import argparse
import json
from pathlib import Path

import pandas as pd

from gold_pipeline.experiment import run_experiment as execute_experiment
from gold_pipeline.experiment_artifacts import save_experiment_artifact
from gold_pipeline.features import FEATURE_COLUMNS


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train, evaluate, and save a gold-direction prediction experiment."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/gc_f.csv"),
        help="Input CSV path, relative to the current working directory.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/gc_f_experiment"),
        help="Directory where the selected model and metadata will be saved.",
    )
    parser.add_argument("--train-end", default="2023-12-31")
    parser.add_argument("--val-end", default="2024-12-31")
    parser.add_argument("--gap", type=int, default=1)
    return parser.parse_args()


def load_data(input_path: Path) -> tuple[pd.DataFrame, str]:
    """Load the historical CSV and identify its instrument."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    data = pd.read_csv(input_path, parse_dates=["date"])

    if data.empty:
        raise ValueError(f"Input CSV contains no data: {input_path}")

    if "ticker" in data.columns:
        tickers = data["ticker"].dropna().astype(str).unique()
        if len(tickers) != 1:
            raise ValueError("Input CSV must contain exactly one distinct, non-null ticker.")
        data_source = tickers[0]
    else:
        data_source = input_path.stem

    return data, data_source


def main() -> None:
    """Run the experiment, report its results, and save its artifact if possible."""
    args = parse_args()
    data, data_source = load_data(args.input)

    result = execute_experiment(
        data,
        train_end=args.train_end,
        val_end=args.val_end,
        gap=args.gap,
    )

    report = {
        "data_source": data_source,
        "input": str(args.input),
        "row_counts": result["row_counts"],
        "date_ranges": result["date_ranges"],
        "selected_model": result["selected_model"],
        "validation_metrics": result["validation_metrics"],
        "test_classification_metrics": result["test_classification_metrics"],
        "test_zero_return_metrics": result["test_zero_return_metrics"],
        "xgboost_best_iteration": result["xgboost_best_iteration"],
    }

    print("=== Experiment Results ===")
    print(json.dumps(report, indent=2, default=str))

    if result["selected_estimator"] is None:
        print(
            "\nNo model artifact saved: the selected candidate "
            f"'{result['selected_model']}' is a rule-based baseline, "
            "not a fitted estimator."
        )
        return

    artifacts = save_experiment_artifact(
        experiment_result=result,
        feature_columns=list(FEATURE_COLUMNS),
        artifact_dir=args.artifact_dir,
        data_source=data_source,
    )

    print("\n=== Saved Artifacts ===")
    print(f"Model:    {artifacts['model_path']}")
    print(f"Metadata: {artifacts['metadata_path']}")


if __name__ == "__main__":
    main()
