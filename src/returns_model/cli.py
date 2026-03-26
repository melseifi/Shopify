from __future__ import annotations

import argparse

import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, roc_auc_score

from returns_model.data import DEFAULT_SPEC, make_synthetic_orders, time_split
from returns_model.model import build_returns_model, pick_threshold_for_precision


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train and evaluate a returns prediction baseline.")
    p.add_argument("--n", type=int, default=5000, help="Number of synthetic orders to generate.")
    p.add_argument("--seed", type=int, default=7, help="RNG seed for data generation.")
    p.add_argument("--test-days", type=int, default=21, help="Size of the time-based test window.")
    p.add_argument(
        "--target-precision",
        type=float,
        default=0.60,
        help="Choose an operating threshold achieving this precision (if possible).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)

    df = make_synthetic_orders(n=args.n, seed=args.seed)
    train_df, test_df = time_split(df, date_col=DEFAULT_SPEC.date_col, test_days=args.test_days)

    model = build_returns_model(DEFAULT_SPEC.numeric_features, DEFAULT_SPEC.categorical_features, target=DEFAULT_SPEC.target)
    model.fit(train_df)

    y_test = test_df[DEFAULT_SPEC.target].to_numpy()
    proba = model.predict_proba_df(test_df)

    roc = roc_auc_score(y_test, proba)
    pr = average_precision_score(y_test, proba)

    thr = pick_threshold_for_precision(y_test, proba, target_precision=args.target_precision)
    y_pred = (proba >= thr).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", zero_division=0)

    # Basic slice sanity check: prevalence and predicted positive rate
    prevalence = float(np.mean(y_test))
    pred_rate = float(np.mean(y_pred))

    print(f"rows: train={len(train_df)} test={len(test_df)}")
    print(f"ROC-AUC: {roc:.4f}")
    print(f"PR-AUC:  {pr:.4f}")
    print(f"threshold: {thr:.4f} (target_precision={args.target_precision:.2f})")
    print(f"precision: {p:.4f} recall: {r:.4f} f1: {f1:.4f}")
    print(f"prevalence: {prevalence:.4f} predicted_positive_rate: {pred_rate:.4f}")

    # Example "production" call: dict -> probability.
    example = {
        "country": "US",
        "device": "mobile",
        "category": "apparel",
        "price": 79.99,
        "shipping_days": 5,
        "customer_age_days": 120,
        "prior_orders": 3,
        "prior_returns": 1,
    }
    print(f"example_predict_proba: {model.predict_proba_one(example):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

