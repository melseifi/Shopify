from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder


def _one_hot_encoder() -> OneHotEncoder:
    """
    scikit-learn renamed `sparse` -> `sparse_output` in newer versions.
    This keeps the project runnable across common interview laptop setups.
    """
    params: dict[str, Any] = {"handle_unknown": "ignore"}
    sig = inspect.signature(OneHotEncoder)
    if "sparse_output" in sig.parameters:
        params["sparse_output"] = False
    else:
        params["sparse"] = False
    return OneHotEncoder(**params)


def build_pipeline(numeric_features: Sequence[str], categorical_features: Sequence[str]) -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", _one_hot_encoder()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, list(numeric_features)),
            ("cat", categorical_transformer, list(categorical_features)),
        ],
        remainder="drop",
    )

    clf = LogisticRegression(max_iter=200, class_weight="balanced")

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", clf),
        ]
    )


def pick_threshold_for_precision(
    y_true: np.ndarray, y_proba: np.ndarray, *, target_precision: float = 0.6
) -> float:
    """
    Pick the smallest threshold achieving precision >= target_precision.
    If unreachable, return 1.0 (predict nothing).
    """
    if not (0.0 < target_precision <= 1.0):
        raise ValueError("target_precision must be in (0, 1]")

    y_true = np.asarray(y_true).astype(int)
    y_proba = np.asarray(y_proba).astype(float)
    if y_true.shape != y_proba.shape:
        raise ValueError("y_true and y_proba must have the same shape")
    if y_true.ndim != 1:
        raise ValueError("y_true and y_proba must be 1D arrays")
    if len(y_true) == 0:
        raise ValueError("empty inputs")

    # precision_recall_curve returns thresholds sorted increasing.
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
    if thresholds.size == 0:
        return 1.0

    # precision has length thresholds+1; align to thresholds by dropping the last entry.
    precision_at_thr = precision[:-1]
    ok = np.where(precision_at_thr >= target_precision)[0]
    if ok.size == 0:
        return 1.0

    return float(thresholds[ok[0]])


@dataclass
class ReturnsModel:
    """
    Thin wrapper to keep feature lists next to the sklearn Pipeline and provide a
    dict-based prediction entrypoint (similar to a production inference call).
    """

    pipeline: Pipeline
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    target: str = "returned"

    @property
    def features(self) -> tuple[str, ...]:
        return (*self.numeric_features, *self.categorical_features)

    def fit(self, df: pd.DataFrame) -> "ReturnsModel":
        missing = [c for c in (self.target, *self.features) if c not in df.columns]
        if missing:
            raise KeyError(f"Missing columns: {missing}")
        X = df.loc[:, list(self.features)]
        y = df.loc[:, self.target].to_numpy()
        self.pipeline.fit(X, y)
        return self

    def predict_proba_df(self, df: pd.DataFrame) -> np.ndarray:
        X = df.loc[:, list(self.features)]
        return self.pipeline.predict_proba(X)[:, 1]

    def predict_proba_one(self, order: Mapping[str, Any]) -> float:
        row: dict[str, Any] = {k: order.get(k, np.nan) for k in self.features}
        X = pd.DataFrame([row], columns=list(self.features))
        return float(self.pipeline.predict_proba(X)[:, 1][0])


def build_returns_model(
    numeric_features: Sequence[str], categorical_features: Sequence[str], *, target: str = "returned"
) -> ReturnsModel:
    return ReturnsModel(
        pipeline=build_pipeline(numeric_features, categorical_features),
        numeric_features=tuple(numeric_features),
        categorical_features=tuple(categorical_features),
        target=target,
    )
