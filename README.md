# Returns Prediction (Pair-Programming Practice)

This is a self-contained ML exercise you can run locally: predict whether an ecommerce order will be returned using only signals available at purchase time.

## Setup

Use your project venv (PyCharm usually creates/uses `.venv`).

```powershell
python -m pip install -r requirements.txt
```

## Run (train + eval)

This repo uses an `src/` layout. If you have not installed the package, run with `PYTHONPATH=src`.

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

## OOP Pairing Practice (Shopping Cart CLI)

Run:

```powershell
$env:PYTHONPATH="src"
python -m shop.cli
```

## What To Discuss In An Interview

Edge cases and risks worth calling out while coding:

- **Leakage**: never use post-purchase signals (refund issued date, delivery scan outcomes, support tickets) when predicting at purchase time.
- **Time split**: use a time-based split to avoid training on “future” behavior.
- **Imbalance**: returns are often rare; include PR-AUC and threshold selection aligned to business constraints.
- **Unknown categories**: new countries/devices/categories should not crash inference (`handle_unknown="ignore"`).
- **Missing values**: robust imputers; explicit checks for empty train/test after splitting.
- **Calibration**: logistic regression is often reasonable, but you might still need probability calibration for decisioning.
- **Monitoring**: drift in category mix/price distribution; performance by slice (country/category/device).
