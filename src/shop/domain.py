from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    price_cents: int

    def __post_init__(self) -> None:
        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("sku must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.price_cents, int):
            raise TypeError("price_cents must be an int")
        if self.price_cents < 0:
            raise ValueError("price_cents must be >= 0")


@dataclass(frozen=True, slots=True)
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int")
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")

    @property
    def sku(self) -> str:
        return self.product.sku

    def line_total_cents(self) -> int:
        return self.product.price_cents * self.quantity


@dataclass(frozen=True, slots=True)
class Order:
    """
    Snapshot of a checkout at a point in time.
    """

    items: tuple[CartItem, ...]
    total_cents: int

    def __post_init__(self) -> None:
        if not isinstance(self.total_cents, int):
            raise TypeError("total_cents must be an int")
        if self.total_cents < 0:
            raise ValueError("total_cents must be >= 0")


class ShoppingCart:
    def __init__(self) -> None:
        self._items_by_sku: dict[str, CartItem] = {}

    def is_empty(self) -> bool:
        return not self._items_by_sku

    def items(self) -> list[CartItem]:
        # Deterministic ordering makes receipts and tests stable.
        return [self._items_by_sku[sku] for sku in sorted(self._items_by_sku)]

    def add_product(self, product: Product, quantity: int) -> None:
        if not isinstance(quantity, int):
            raise TypeError("quantity must be an int")
        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        existing = self._items_by_sku.get(product.sku)
        if existing is None:
            self._items_by_sku[product.sku] = CartItem(product=product, quantity=quantity)
            return

        if existing.product.price_cents != product.price_cents or existing.product.name != product.name:
            raise ValueError(f"Product mismatch for existing sku {product.sku!r}")

        self._items_by_sku[product.sku] = CartItem(product=product, quantity=existing.quantity + quantity)

    def remove_sku(self, sku: str, quantity: int) -> None:
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("sku must be a non-empty string")
        if not isinstance(quantity, int):
            raise TypeError("quantity must be an int")
        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        existing = self._items_by_sku.get(sku)
        if existing is None:
            raise KeyError(f"sku not in cart: {sku!r}")

        if quantity > existing.quantity:
            raise ValueError("cannot remove more than existing quantity")

        remaining = existing.quantity - quantity
        if remaining == 0:
            del self._items_by_sku[sku]
        else:
            self._items_by_sku[sku] = CartItem(product=existing.product, quantity=remaining)

    def total_cents(self) -> int:
        return sum(item.line_total_cents() for item in self._items_by_sku.values())

    def clear(self) -> None:
        self._items_by_sku.clear()

    def checkout(self) -> Order:
        if self.is_empty():
            raise ValueError("cannot checkout an empty cart")

        snapshot_items = tuple(CartItem(product=item.product, quantity=item.quantity) for item in self.items())
        total = sum(item.line_total_cents() for item in snapshot_items)
        order = Order(items=snapshot_items, total_cents=total)
        self.clear()
        return order

