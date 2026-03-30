# Pair Programming Practice (Shopify-Style)

This repo contains a small, self-contained V1 inventory management system you can use to practice a 75-minute pair-programming interview in Python.

## Setup

Use your project venv (PyCharm usually creates/uses `.venv`).

```powershell
python -m pip install -r requirements.txt
```

## OOP Exercise: Inventory Management (V1)

Run:

```powershell
$env:PYTHONPATH="src"
python -m inventory.cli
```

Core logic lives in `src/inventory/domain.py` and is covered by unit tests in `tests/test_inventory_v1.py`.

## Tests

```powershell
$env:PYTHONPATH="src"
pytest -q
```

## What To Discuss In An Interview

High-signal points to narrate while pairing:

- OOP: invariants, input validation, separating domain logic from CLI parsing, and tests for tricky cases.
- Scalability: persistence boundary (DB), concurrency/locking, multi-location inventory, reservations/backorders, idempotency for stock events.
