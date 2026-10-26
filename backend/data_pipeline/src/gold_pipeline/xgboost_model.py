"""Train an XGBoost classifier using a chronological validation set."""

import pandas as pd
from xgboost import XGBClassifier

from gold_pipeline.features import FEATURE_COLUMNS


def fit_xgboost_classifier(
    train_features: pd.DataFrame,
    train_directions: pd.Series,
    val_features: pd.DataFrame,
    val_directions: pd.Series,
    *,
    n_estimators: int = 500,
    early_stopping_rounds: int = 30,
    random_state: int = 42,
) -> XGBClassifier:
    """Fit XGBoost on training data and stop using validation performance."""
    if train_features.empty or val_features.empty:
        raise ValueError("Training and validation features cannot be empty.")

    if train_directions.empty or val_directions.empty:
        raise ValueError("Training and validation labels cannot be empty.")

    if len(train_features) != len(train_directions):
        raise ValueError("Training features and labels must have the same length.")

    if len(val_features) != len(val_directions):
        raise ValueError("Validation features and labels must have the same length.")

    if train_directions.nunique() < 2:
        raise ValueError("Training labels must contain both direction classes.")

    if not train_directions.isin([0, 1]).all():
        raise ValueError("Training labels must contain only 0 and 1.")

    if not val_directions.isin([0, 1]).all():
        raise ValueError("Validation labels must contain only 0 and 1.")

    if n_estimators < 1:
        raise ValueError("n_estimators must be positive.")

    if early_stopping_rounds < 1:
        raise ValueError("early_stopping_rounds must be positive.")

    for name, frame in (
        ("Training", train_features),
        ("Validation", val_features),
    ):
        missing = set(FEATURE_COLUMNS) - set(frame.columns)
        if missing:
            raise ValueError(f"{name} features are missing columns: {', '.join(sorted(missing))}")

    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=n_estimators,
        learning_rate=0.03,
        max_depth=3,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        tree_method="hist",
        early_stopping_rounds=early_stopping_rounds,
        random_state=random_state,
        n_jobs=1,
    )

    model.fit(
        train_features[FEATURE_COLUMNS],
        train_directions,
        eval_set=[
            (
                val_features[FEATURE_COLUMNS],
                val_directions,
            )
        ],
        verbose=False,
    )

    return model
