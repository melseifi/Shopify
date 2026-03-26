import pytest

from shop.domain import CartItem, Product, ShoppingCart


def test_add_product_creates_item_and_total():
    cart = ShoppingCart()
    tshirt = Product(sku="TSHIRT", name="T-Shirt", price_cents=1999)
    cart.add_product(tshirt, 2)

    items = cart.items()
    assert len(items) == 1
    assert items[0].sku == "TSHIRT"
    assert items[0].quantity == 2
    assert cart.total_cents() == 3998


def test_add_product_same_sku_aggregates_quantity():
    cart = ShoppingCart()
    mug = Product(sku="MUG", name="Coffee Mug", price_cents=1299)
    cart.add_product(mug, 1)
    cart.add_product(mug, 3)
    assert cart.items()[0].quantity == 4
    assert cart.total_cents() == 4 * 1299


def test_add_product_rejects_non_positive_quantity():
    cart = ShoppingCart()
    p = Product(sku="A", name="A", price_cents=100)
    with pytest.raises(ValueError):
        cart.add_product(p, 0)
    with pytest.raises(ValueError):
        cart.add_product(p, -1)


def test_remove_sku_reduces_and_deletes():
    cart = ShoppingCart()
    p = Product(sku="HAT", name="Hat", price_cents=2500)
    cart.add_product(p, 3)
    cart.remove_sku("HAT", 1)
    assert cart.items()[0].quantity == 2
    cart.remove_sku("HAT", 2)
    assert cart.is_empty()


def test_remove_sku_unknown_or_too_many_errors():
    cart = ShoppingCart()
    with pytest.raises(KeyError):
        cart.remove_sku("NOPE", 1)

    p = Product(sku="X", name="X", price_cents=100)
    cart.add_product(p, 1)
    with pytest.raises(ValueError):
        cart.remove_sku("X", 2)


def test_checkout_creates_snapshot_and_clears_cart():
    cart = ShoppingCart()
    a = Product(sku="A", name="A", price_cents=199)
    b = Product(sku="B", name="B", price_cents=500)
    cart.add_product(a, 2)
    cart.add_product(b, 1)

    order = cart.checkout()
    assert cart.is_empty()
    assert order.total_cents == 2 * 199 + 1 * 500
    assert [i.sku for i in order.items] == ["A", "B"]

    # Mutating the cart after checkout must not mutate the order snapshot.
    cart.add_product(a, 1)
    assert order.total_cents == 2 * 199 + 1 * 500
    assert order.items[0].quantity == 2


def test_checkout_empty_cart_errors():
    cart = ShoppingCart()
    with pytest.raises(ValueError):
        cart.checkout()


def test_cart_item_validation():
    p = Product(sku="A", name="A", price_cents=100)
    with pytest.raises(ValueError):
        CartItem(product=p, quantity=0)

