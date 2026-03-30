# Pair Programming Practice (Shopify-Style)

This repo contains two small, self-contained exercises you can use to practice a 75-minute pair-programming interview in Python:

- OOP Shopping Cart CLI (recommended for the "design + implement + test" flow)
- ML Returns Prediction baseline (optional, for ML-flavored discussion)

## Setup

Use your project venv (PyCharm usually creates/uses `.venv`).

```powershell
python -m pip install -r requirements.txt
```

## OOP Exercise: Shopping Cart CLI

Run:

```powershell
$env:PYTHONPATH="src"
python -m shop.cli
```

Commands (in the app): `list`, `add <SKU> <QTY>`, `remove <SKU> <QTY>`, `view`, `checkout`, `quit`.

Core logic lives in `src/shop/domain.py` and is covered by unit tests in `tests/test_shop_domain.py`.

## OOP Exercise: Inventory Management (V1)

Run:

```powershell
$env:PYTHONPATH="src"
python -m inventory.cli
```

Core logic lives in `src/inventory/domain.py` and is covered by unit tests in `tests/test_inventory_v1.py`.

## ML Exercise: Returns Prediction (train + eval)

Run:

```powershell
$env:PYTHONPATH="src"
python -m returns_model.cli
```

Optional args:

```powershell
$env:PYTHONPATH="src"
python -m returns_model.cli --n 8000 --seed 7 --test-days 21 --target-precision 0.60
```

## Tests

```powershell
$env:PYTHONPATH="src"
pytest -q
```

## What To Discuss In An Interview

High-signal points to narrate while pairing:

- OOP: invariants, input validation, separating domain logic from CLI parsing, and tests for tricky cases (remove too many, empty checkout, duplicates).
- ML leakage: never use post-purchase signals (refund issued date, delivery scan outcomes, support tickets) when predicting at purchase time.
- ML time split: use a time-based split to avoid training on "future" behavior.
- ML imbalance: include PR-AUC and threshold selection aligned to business constraints.
- ML robustness: unknown categories and missing values should not crash inference.
