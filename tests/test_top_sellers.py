import pytest

from sales_analytics.top_sellers import Sale, top_n_best_selling_products


def test_top_n_basic_aggregation_and_sorting():
    sales = [
        Sale("A", 2),
        Sale("B", 5),
        Sale("A", 3),
        Sale("C", 5),
    ]
    # Totals: A=5, B=5, C=5; tie-break by product_id asc.
    assert top_n_best_selling_products(sales, 2) == [("A", 5), ("B", 5)]


def test_top_n_accepts_tuple_input():
    sales = [("B", 1), ("A", 10), ("B", 2)]
    assert top_n_best_selling_products(sales, 10) == [("A", 10), ("B", 3)]


def test_top_n_empty_and_non_positive_n():
    assert top_n_best_selling_products([], 3) == []
    assert top_n_best_selling_products([("A", 1)], 0) == []
    assert top_n_best_selling_products([("A", 1)], -1) == []


def test_top_n_validates_inputs():
    with pytest.raises(TypeError):
        top_n_best_selling_products([("A", 1)], 1.5)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        top_n_best_selling_products([("", 1)], 1)

    with pytest.raises(TypeError):
        top_n_best_selling_products([("A", "1")], 1)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        top_n_best_selling_products([("A", -1)], 1)

