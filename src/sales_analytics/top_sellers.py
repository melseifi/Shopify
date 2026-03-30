from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True, slots=True)
class Sale:
    """
    Minimal V1 sale record.

    `units` is the number of units sold for `product_id` (non-negative int).
    """

    product_id: str
    units: int

    def __post_init__(self) -> None:
        if not isinstance(self.product_id, str) or not self.product_id.strip():
            raise ValueError("product_id must be a non-empty string")
        if not isinstance(self.units, int):
            raise TypeError("units must be an int")
        if self.units < 0:
            # V1: treat negative units as invalid input rather than "returns".
            raise ValueError("units must be >= 0")


def top_n_best_selling_products(sales: Iterable[Sale], n: int) -> List[Tuple[str, int]]:
    """
    Return the top N best-selling products by units sold.

    Output is sorted by:
    1) total units sold (descending)
    2) product_id (ascending) as a deterministic tie-breaker

    For n <= 0 or empty input, returns [].

    Notes:
    - This is a simple V1 implementation: it aggregates per product, then sorts all products.
      For very large numbers of unique products, you can optimize to O(U log N) with a heap.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if n <= 0:
        return []

    totals: dict[str, int] = defaultdict(int)
    for s in sales:
        # Accept either Sale objects or (product_id, units) tuples for convenience.
        if isinstance(s, Sale):
            product_id = s.product_id.strip()
            units = s.units
        else:
            try:
                product_id, units = s  # type: ignore[misc]
            except Exception as e:  # noqa: BLE001
                raise TypeError("sales must contain Sale or (product_id, units) pairs") from e

            if not isinstance(product_id, str) or not product_id.strip():
                raise ValueError("product_id must be a non-empty string")
            if not isinstance(units, int):
                raise TypeError("units must be an int")
            if units < 0:
                raise ValueError("units must be >= 0")
            product_id = product_id.strip()

        totals[product_id] += units

    if not totals:
        return []

    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[: min(n, len(ranked))]

