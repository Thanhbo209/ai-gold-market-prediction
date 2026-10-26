"""Construct past-only features for daily gold-price data."""

import pandas as pd

FEATURE_COLUMNS = [
    "return_1",
    "return_2",
    "return_5",
    "return_10",
    "return_20",
    "volatility_5",
    "volatility_20",
    "distance_sma_20",
    "distance_sma_50",
    "intraday_range",
    "drawdown_50",
    "rsi_14",
    "day_of_week",
]

REQUIRED_COLUMNS = {"date", "open", "high", "low", "close"}


def build_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build features using only current and historical observations."""
    if data.empty:
        raise ValueError("Cannot build features from empty data.")

    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    frame = data[["date", "open", "high", "low", "close"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")

    if frame["date"].isna().any():
        raise ValueError("Dates contain missing or invalid values.")

    if frame["date"].duplicated().any():
        raise ValueError("Duplicate dates are not allowed.")

    if not frame["date"].is_monotonic_increasing:
        raise ValueError("Dates must be sorted in ascending order.")

    price_columns = ["open", "high", "low", "close"]
    for column in price_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    if frame[price_columns].isna().any().any():
        raise ValueError("OHLC prices must be numeric and non-missing.")

    if (frame[price_columns] <= 0).any().any():
        raise ValueError("OHLC prices must be greater than zero.")

    close = frame["close"]
    daily_return = close.pct_change(fill_method=None)

    features = pd.DataFrame(index=frame.index)
    features["date"] = frame["date"]

    # Returns over trailing observation windows, including the current close.
    for period in (1, 2, 5, 10, 20):
        features[f"return_{period}"] = close.pct_change(
            periods=period,
            fill_method=None,
        )

    # Volatility of daily returns over trailing windows.
    features["volatility_5"] = daily_return.rolling(5).std(ddof=0)
    features["volatility_20"] = daily_return.rolling(20).std(ddof=0)

    # Relative distance from trailing moving averages.
    features["distance_sma_20"] = close / close.rolling(20).mean() - 1
    features["distance_sma_50"] = close / close.rolling(50).mean() - 1

    # Intraday range as a proportion of the closing price.
    features["intraday_range"] = (frame["high"] - frame["low"]) / close

    # Drawdown relative to the trailing 50-observation high.
    trailing_peak = close.rolling(50).max()
    features["drawdown_50"] = close / trailing_peak - 1

    # RSI-style momentum based on 14 price changes.
    change = close.diff()
    average_gain = change.clip(lower=0).rolling(14).mean()
    average_loss = -change.clip(upper=0).rolling(14).mean()

    relative_strength = average_gain.div(average_loss.where(average_loss != 0))
    rsi = 100 - 100 / (1 + relative_strength)
    rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100.0)
    rsi = rsi.mask((average_loss == 0) & (average_gain == 0), 50.0)
    features["rsi_14"] = rsi

    features["day_of_week"] = features["date"].dt.dayofweek

    # Explicitly discard warm-up observations with incomplete rolling features.
    features = features.dropna(subset=FEATURE_COLUMNS)

    return features[["date", *FEATURE_COLUMNS]].reset_index(drop=True)
