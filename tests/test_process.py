import pytest
from unittest.mock import patch

from src.utils import calc
from src.process import proc, get_discount

# Tests for calc()

def test_calc_negative():
    """calc() currently allows negative calculation results."""
    assert calc(-50, 0.15) == -7.5


def test_calc_zero_amount():
    """Zero amount should produce zero result."""
    assert calc(0, 0.15) == 0

# Tests for get_discount()

def test_discount_zero_amount():
    """Zero amount should not produce a discount."""
    assert get_discount(0, 3) == 0


def test_discount_negative_amount():
    """Negative amount should not produce a negative discount."""
    assert get_discount(-100, 3) == 0


def test_discount_regular_user():
    """Regular users should not receive a discount."""
    assert get_discount(1500, 2) == 0


def test_discount_premium_below_threshold():
    """Premium users should not receive a discount below 500."""
    assert get_discount(400, 3) == 0


def test_discount_premium_middle_threshold():
    """Premium users receive 3% discount for amounts above 500."""
    assert get_discount(600, 3) == 18.0


def test_discount_premium_high_threshold():
    """Premium users receive 5% discount for amounts above 1000."""
    assert get_discount(1200, 3) == 60.0

# Tests for proc()

def test_proc_rejects_negative_net():
    """proc() must not save orders with negative net."""

    orders = [
        {
            "id": 1,
            "user_id": 1,
            "product_id": 1,
            "amount": -50,
            "status": "paid",
            "date": "2026-10-17"
        }
    ]

    users = [
        {
            "id": 1,
            "name": "Test User",
            "role": 3
        }
    ]

    products = [
        {
            "id": 1,
            "name": "Test Product"
        }
    ]

    def mock_get_data(table):
        data = {
            "orders": orders,
            "users": users,
            "products": products
        }
        return data[table]

    with patch("src.process.get_data", side_effect=mock_get_data), \
         patch("src.process.save") as mock_save:

        result = proc()

        saved_orders = mock_save.call_args_list[0].args[1]

        # Order with negative net must not be saved.
        assert not any(
            order.get("order_id") == 1
            for order in saved_orders
        )

        # The order must be reported as an error.
        assert any(
            error["order_id"] == 1
            for error in result["summary"]["errors"]
        )


def test_proc_accepts_zero_net():
    """proc() should accept an order with net equal to zero."""

    orders = [
        {
            "id": 2,
            "user_id": 1,
            "product_id": 1,
            "amount": 0,
            "status": "paid",
            "date": "2026-10-17"
        }
    ]

    users = [
        {
            "id": 1,
            "name": "Test User",
            "role": 2
        }
    ]

    products = [
        {
            "id": 1,
            "name": "Test Product"
        }
    ]

    def mock_get_data(table):
        data = {
            "orders": orders,
            "users": users,
            "products": products
        }
        return data[table]

    with patch("src.process.get_data", side_effect=mock_get_data), \
         patch("src.process.save"):

        result = proc()

        assert len(result["orders"]) == 1
        assert result["orders"][0]["net"] == 0
        assert result["orders"][0]["status"] == "processed"
