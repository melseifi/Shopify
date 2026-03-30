from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable


class InventoryError(Exception):
    pass


class UnknownSKUError(InventoryError):
    pass


class DuplicateSKUError(InventoryError):
    pass


class InvalidQuantityError(InventoryError):
    pass


class InsufficientStockError(InventoryError):
    pass


class TransactionType(str, Enum):
    RECEIVE = "RECEIVE"
    SHIP = "SHIP"
    ADJUST = "ADJUST"


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("sku must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")


@dataclass(frozen=True, slots=True)
class InventoryTransaction:
    type: TransactionType
    sku: str
    delta: int
    timestamp: datetime
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.delta, int):
            raise TypeError("delta must be an int")
        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("sku must be a non-empty string")
        if self.delta == 0:
            raise ValueError("delta must be non-zero")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Inventory:
    """
    V1: single location, in-memory, SKU-based stock, no reservations/backorders.
    """

    def __init__(self, *, clock: Callable[[], datetime] = _utcnow) -> None:
        self._clock = clock
        self._products: dict[str, Product] = {}
        self._on_hand: dict[str, int] = {}
        self._tx: list[InventoryTransaction] = []

    def add_product(self, sku: str, name: str) -> None:
        sku = sku.strip() if isinstance(sku, str) else sku
        if not isinstance(sku, str) or not sku:
            raise ValueError("sku must be a non-empty string")
        if sku in self._products:
            raise DuplicateSKUError(f"sku already exists: {sku!r}")
        product = Product(sku=sku, name=name)
        self._products[sku] = product
        self._on_hand[sku] = 0

    def receive_stock(self, sku: str, qty: int, note: str = "") -> None:
        sku = self._normalize_sku(sku)
        qty = self._validate_positive_qty(qty)
        self._require_known_sku(sku)
        self._apply_delta(TransactionType.RECEIVE, sku, qty, note)

    def ship_stock(self, sku: str, qty: int, note: str = "") -> None:
        sku = self._normalize_sku(sku)
        qty = self._validate_positive_qty(qty)
        self._require_known_sku(sku)
        if qty > self._on_hand[sku]:
            raise InsufficientStockError(f"insufficient stock for {sku!r}: on_hand={self._on_hand[sku]} qty={qty}")
        self._apply_delta(TransactionType.SHIP, sku, -qty, note)

    def adjust_stock(self, sku: str, delta: int, note: str = "") -> None:
        sku = self._normalize_sku(sku)
        if not isinstance(delta, int):
            raise InvalidQuantityError("delta must be an int")
        if delta == 0:
            raise InvalidQuantityError("delta must be non-zero")
        self._require_known_sku(sku)
        if delta < 0 and (-delta) > self._on_hand[sku]:
            raise InsufficientStockError(
                f"insufficient stock for {sku!r}: on_hand={self._on_hand[sku]} delta={delta}"
            )
        self._apply_delta(TransactionType.ADJUST, sku, delta, note)

    def get_on_hand(self, sku: str) -> int:
        sku = self._normalize_sku(sku)
        self._require_known_sku(sku)
        return self._on_hand[sku]

    def list_inventory(self) -> list[tuple[str, int]]:
        return [(sku, self._on_hand[sku]) for sku in sorted(self._products)]

    def transactions(self) -> tuple[InventoryTransaction, ...]:
        return tuple(self._tx)

    def _apply_delta(self, ttype: TransactionType, sku: str, delta: int, note: str) -> None:
        new_qty = self._on_hand[sku] + delta
        if new_qty < 0:
            raise InsufficientStockError(f"operation would make on_hand negative for {sku!r}: {new_qty}")

        tx = InventoryTransaction(
            type=ttype,
            sku=sku,
            delta=delta,
            timestamp=self._clock(),
            note=note or "",
        )
        self._on_hand[sku] = new_qty
        self._tx.append(tx)

    @staticmethod
    def _normalize_sku(sku: str) -> str:
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("sku must be a non-empty string")
        return sku.strip()

    @staticmethod
    def _validate_positive_qty(qty: int) -> int:
        if not isinstance(qty, int):
            raise InvalidQuantityError("qty must be an int")
        if qty <= 0:
            raise InvalidQuantityError("qty must be > 0")
        return qty

    def _require_known_sku(self, sku: str) -> None:
        if sku not in self._products:
            raise UnknownSKUError(f"unknown sku: {sku!r}")

