from __future__ import annotations

import shlex
from datetime import datetime

from inventory.domain import (
    Inventory,
    InventoryError,
)


def _print_help() -> None:
    print("Commands:")
    print("  add_product <SKU> <NAME...>")
    print("  receive     <SKU> <QTY> [NOTE...]")
    print("  ship        <SKU> <QTY> [NOTE...]")
    print("  adjust      <SKU> <DELTA> [NOTE...]   (DELTA can be negative)")
    print("  on_hand     <SKU>")
    print("  list")
    print("  tx")
    print("  help")
    print("  quit")


def main() -> int:
    inv = Inventory()
    _print_help()

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
                _print_help()
            elif cmd == "add_product":
                if len(args) < 2:
                    raise ValueError("usage: add_product <SKU> <NAME...>")
                sku = args[0]
                name = " ".join(args[1:])
                inv.add_product(sku, name)
                print(f"ok: added {sku!r}")
            elif cmd in {"receive", "ship"}:
                if len(args) < 2:
                    raise ValueError(f"usage: {cmd} <SKU> <QTY> [NOTE...]")
                sku = args[0]
                qty = int(args[1])
                note = " ".join(args[2:]) if len(args) > 2 else ""
                if cmd == "receive":
                    inv.receive_stock(sku, qty, note=note)
                else:
                    inv.ship_stock(sku, qty, note=note)
                print("ok")
            elif cmd == "adjust":
                if len(args) < 2:
                    raise ValueError("usage: adjust <SKU> <DELTA> [NOTE...]")
                sku = args[0]
                delta = int(args[1])
                note = " ".join(args[2:]) if len(args) > 2 else ""
                inv.adjust_stock(sku, delta, note=note)
                print("ok")
            elif cmd == "on_hand":
                if len(args) != 1:
                    raise ValueError("usage: on_hand <SKU>")
                sku = args[0]
                print(inv.get_on_hand(sku))
            elif cmd == "list":
                rows = inv.list_inventory()
                if not rows:
                    print("(no products)")
                for sku, on_hand in rows:
                    print(f"{sku}\ton_hand={on_hand}")
            elif cmd == "tx":
                tx = inv.transactions()
                if not tx:
                    print("(no transactions)")
                for t in tx:
                    ts = t.timestamp.astimezone(t.timestamp.tzinfo).isoformat()
                    note = f"\t{t.note}" if t.note else ""
                    print(f"{ts}\t{t.type}\t{t.sku}\t{t.delta}{note}")
            else:
                print(f"unknown command: {cmd!r} (try: help)")
        except InventoryError as e:
            print(f"error: {e}")
        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    raise SystemExit(main())

