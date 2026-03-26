from __future__ import annotations

import shlex

from shop.domain import Product, ShoppingCart


def format_cents(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"


def print_cart(cart: ShoppingCart) -> None:
    if cart.is_empty():
        print("(cart is empty)")
        return
    for item in cart.items():
        unit = format_cents(item.product.price_cents)
        line = format_cents(item.line_total_cents())
        print(f"{item.sku}\t{item.product.name}\tqty={item.quantity}\tunit={unit}\tline={line}")
    print(f"TOTAL\t{format_cents(cart.total_cents())}")


def main() -> int:
    # In-memory catalog for V1. In a real app this could be a DB/API lookup.
    catalog: dict[str, Product] = {
        "TSHIRT": Product(sku="TSHIRT", name="T-Shirt", price_cents=1999),
        "MUG": Product(sku="MUG", name="Coffee Mug", price_cents=1299),
        "HAT": Product(sku="HAT", name="Cap", price_cents=2499),
    }

    cart = ShoppingCart()

    print("Commands: list | add <SKU> <QTY> | remove <SKU> <QTY> | view | checkout | help | quit")
    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            print()
            return 0

        if not raw:
            continue

        try:
            parts = shlex.split(raw)
        except ValueError as e:
            print(f"error: {e}")
            continue

        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd in {"quit", "exit"}:
                return 0
            if cmd == "help":
                print("Commands: list | add <SKU> <QTY> | remove <SKU> <QTY> | view | checkout | help | quit")
            elif cmd == "list":
                for p in catalog.values():
                    print(f"{p.sku}\t{p.name}\t{format_cents(p.price_cents)}")
            elif cmd == "add":
                if len(args) != 2:
                    raise ValueError("usage: add <SKU> <QTY>")
                sku, qty_s = args
                product = catalog.get(sku)
                if product is None:
                    raise KeyError(f"unknown sku: {sku!r}")
                cart.add_product(product, int(qty_s))
            elif cmd == "remove":
                if len(args) != 2:
                    raise ValueError("usage: remove <SKU> <QTY>")
                sku, qty_s = args
                cart.remove_sku(sku, int(qty_s))
            elif cmd == "view":
                print_cart(cart)
            elif cmd == "checkout":
                order = cart.checkout()
                for item in order.items:
                    unit = format_cents(item.product.price_cents)
                    line = format_cents(item.line_total_cents())
                    print(f"{item.sku}\t{item.product.name}\tqty={item.quantity}\tunit={unit}\tline={line}")
                print(f"TOTAL\t{format_cents(order.total_cents)}")
                print("(checked out)")
            else:
                print(f"unknown command: {cmd!r} (try: help)")
        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    raise SystemExit(main())

