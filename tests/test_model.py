import numpy as np
import pytest

from returns_model.data import DEFAULT_SPEC, make_synthetic_orders, time_split
from returns_model.model import build_returns_model, pick_threshold_for_precision


def test_pick_threshold_for_precision_basic():
    y_true = np.array([0, 0, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.8, 0.9])
    thr = pick_threshold_for_precision(y_true, y_proba, target_precision=1.0)
    assert 0.8 <= thr <= 0.9


def test_pick_threshold_for_precision_unreachable_returns_1():
    y_true = np.array([0, 0, 0, 1])
    y_proba = np.array([0.9, 0.8, 0.7, 0.6])  # negatives look more positive than the positive
    thr = pick_threshold_for_precision(y_true, y_proba, target_precision=0.9)
    assert thr == 1.0


def test_model_trains_and_predicts_and_handles_unknowns_and_missing():
    df = make_synthetic_orders(n=3000, seed=4)
    train, test = time_split(df, test_days=14)

    model = build_returns_model(DEFAULT_SPEC.numeric_features, DEFAULT_SPEC.categorical_features)
    model.fit(train)

    proba = model.predict_proba_df(test)
    assert proba.shape == (len(test),)
    assert np.isfinite(proba).all()
    assert ((0.0 <= proba) & (proba <= 1.0)).all()

    # Unknown category/country + missing numeric should not crash.
    p = model.predict_proba_one(
        {
            "country": "ZZ",
            "device": "mobile",
            "category": "never_seen_before",
            "price": None,
            "shipping_days": 3,
            "customer_age_days": 10,
            "prior_orders": 0,
            "prior_returns": 0,
        }
    )
    assert 0.0 <= p <= 1.0


def test_model_rejects_missing_columns_on_fit():
    df = make_synthetic_orders(n=100, seed=5).drop(columns=["price"])
    model = build_returns_model(DEFAULT_SPEC.numeric_features, DEFAULT_SPEC.categorical_features)
    with pytest.raises(KeyError):
        model.fit(df)

