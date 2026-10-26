"""Run direction inference from a historical gold CSV."""

import argparse
import json
from pathlib import Path

import pandas as pd

from gold_pipeline.prediction import predict_latest_direction


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Predict the next-observation gold price direction."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/gc_f.csv"),
        help="Historical OHLC CSV.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/gc_f_experiment"),
        help="Directory containing model.joblib and metadata.json.",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Input CSV not found: {args.input}")

    data = pd.read_csv(args.input, parse_dates=["date"])
    result = predict_latest_direction(data, args.artifact_dir)

    print("=== Latest Gold Direction Prediction ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
