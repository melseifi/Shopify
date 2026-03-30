from datetime import datetime, timezone

import pytest

from inventory.domain import (
    InsufficientStockError,
    Inventory,
    TransactionType,
    UnknownSKUError,
)


def test_receive_then_ship_updates_on_hand_and_logs_transactions():
    now = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    inv = Inventory(clock=lambda: now)
    inv.add_product("A", "Widget A")

    inv.receive_stock("A", 10, note="initial")
    inv.ship_stock("A", 3, note="order-123")

    assert inv.get_on_hand("A") == 7

    tx = inv.transactions()
    assert len(tx) == 2
    assert tx[0].type == TransactionType.RECEIVE
    assert tx[0].sku == "A"
    assert tx[0].delta == 10
    assert tx[0].timestamp == now

    assert tx[1].type == TransactionType.SHIP
    assert tx[1].sku == "A"
    assert tx[1].delta == -3
    assert tx[1].timestamp == now


def test_ship_insufficient_raises_and_does_not_mutate():
    now = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    inv = Inventory(clock=lambda: now)
    inv.add_product("A", "Widget A")
    inv.receive_stock("A", 2)
    before_tx = inv.transactions()

    with pytest.raises(InsufficientStockError):
        inv.ship_stock("A", 5)

    assert inv.get_on_hand("A") == 2
    assert inv.transactions() == before_tx


def test_unknown_sku_errors():
    inv = Inventory()
    with pytest.raises(UnknownSKUError):
        inv.receive_stock("NOPE", 1)

