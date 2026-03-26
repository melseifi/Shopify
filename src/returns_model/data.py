from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DatasetSpec:
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    target: str = "returned"
    date_col: str = "order_date"

    @property
    def features(self) -> tuple[str, ...]:
        return (*self.numeric_features, *self.categorical_features)


DEFAULT_SPEC = DatasetSpec(
    numeric_features=("price", "shipping_days", "customer_age_days", "prior_orders", "prior_returns"),
    categorical_features=("country", "device", "category"),
)


def make_synthetic_orders(n: int = 5000, seed: int = 7, start: date = date(2025, 1, 1)) -> pd.DataFrame:
    """
    Generate a synthetic ecommerce orders dataset.

    The label `returned` is generated from a hidden logistic model to make the task learnable.
    All features are intended to be available at purchase time.
    """
    if n <= 0:
        raise ValueError("n must be > 0")

    rng = np.random.default_rng(seed)

    order_day = rng.integers(0, 120, size=n)
    order_date = np.array([start + timedelta(days=int(d)) for d in order_day], dtype=object)

    country = rng.choice(["US", "CA", "GB", "DE", "FR"], size=n, p=[0.5, 0.2, 0.12, 0.1, 0.08])
    device = rng.choice(["mobile", "desktop"], size=n, p=[0.65, 0.35])
    category = rng.choice(["apparel", "electronics", "home", "beauty"], size=n, p=[0.45, 0.2, 0.25, 0.1])

    price = rng.lognormal(mean=3.6, sigma=0.6, size=n)  # skewed: roughly $20-$200
    shipping_days = rng.integers(1, 8, size=n)
    customer_age_days = rng.integers(0, 2000, size=n)
    prior_returns = rng.poisson(lam=0.4, size=n)
    prior_orders = np.maximum(prior_returns + rng.poisson(lam=2.0, size=n), 0)

    # Inject missingness
    price = price.astype(float)
    price[rng.random(n) < 0.02] = np.nan
    category = category.astype(object)
    category[rng.random(n) < 0.03] = None

    df = pd.DataFrame(
        {
            "order_date": order_date,
            "country": country,
            "device": device,
            "category": category,
            "price": price,
            "shipping_days": shipping_days,
            "customer_age_days": customer_age_days,
            "prior_orders": prior_orders,
            "prior_returns": prior_returns,
        }
    )

    # Hidden data-generating process (unknown to the model).
    logit = (
        -3.0
        + 0.012 * (shipping_days - 3)
        + 0.9 * (prior_returns > 0)
        + 0.25 * (device == "mobile")
        + 0.35 * (df["category"].fillna("unknown") == "apparel")
        + 0.0025 * (np.nan_to_num(price) - 60)
    )

    logit += np.select(
        [country == "US", country == "CA", country == "GB", country == "DE", country == "FR"],
        [0.0, 0.15, 0.1, 0.05, 0.08],
        default=0.0,
    )

    p = 1 / (1 + np.exp(-logit))
    y = rng.binomial(1, p)
    df["returned"] = y.astype(int)
    return df


def time_split(
    df: pd.DataFrame, *, date_col: str = DEFAULT_SPEC.date_col, test_days: int = 21
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split into (train, test) using the last `test_days` (inclusive) by `date_col` as test.

    Raises on degenerate splits where train or test would be empty.
    """
    if test_days <= 0:
        raise ValueError("test_days must be > 0")
    if date_col not in df.columns:
        raise KeyError(f"Missing date column: {date_col!r}")

    if len(df) == 0:
        raise ValueError("df is empty")

    dates = pd.to_datetime(df[date_col], errors="coerce")
    if dates.isna().all():
        raise ValueError(f"All values in {date_col!r} failed datetime parsing")

    max_date = dates.max()
    test_start = max_date - pd.Timedelta(days=test_days - 1)

    is_test = dates >= test_start
    test_df = df.loc[is_test].copy()
    train_df = df.loc[~is_test].copy()

    if len(test_df) == 0:
        raise ValueError("time_split produced an empty test set (check test_days)")
    if len(train_df) == 0:
        raise ValueError("time_split produced an empty train set (check test_days)")

    return train_df, test_df

