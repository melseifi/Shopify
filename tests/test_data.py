import pandas as pd
import pytest

from returns_model.data import make_synthetic_orders, time_split


def test_make_synthetic_orders_has_expected_columns():
    df = make_synthetic_orders(n=10, seed=1)
    assert "returned" in df.columns
    assert "order_date" in df.columns
    assert set(df["returned"].unique()).issubset({0, 1})


def test_time_split_last_window_is_test():
    df = make_synthetic_orders(n=2000, seed=2)
    train, test = time_split(df, test_days=10)

    train_dates = pd.to_datetime(train["order_date"])
    test_dates = pd.to_datetime(test["order_date"])

    assert train_dates.max() < test_dates.min()

    max_date = pd.to_datetime(df["order_date"]).max()
    test_start = max_date - pd.Timedelta(days=9)
    assert (test_dates >= test_start).all()


def test_time_split_rejects_bad_inputs():
    df = make_synthetic_orders(n=50, seed=3)
    with pytest.raises(ValueError):
        time_split(df, test_days=0)
    with pytest.raises(KeyError):
        time_split(df, date_col="nope")

    # Force degenerate split by making all dates the same.
    df2 = df.copy()
    df2["order_date"] = df2["order_date"].iloc[0]
    with pytest.raises(ValueError):
        time_split(df2, test_days=1)

