import pytest
from src import analytics


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset global state before and after each test."""
    analytics.reset_stats()
    yield
    analytics.reset_stats()

# 1. calc_metrics

def test_calc_metrics_empty_data():
    """Empty data returns NO_DATA error."""
    code, result = analytics.calc_metrics([], 1)

    assert code == analytics.ERROR_CODE_NO_DATA
    assert result is None
    assert analytics.GLOBAL_STATS["calls"] == 1
    assert analytics.GLOBAL_STATS["errors"] == 1


def test_calc_metrics_daily():
    """Daily metrics calculate total, average and count."""
    data = [
        {"amount": 100},
        {"amount": 200},
        {"amount": 300}
    ]

    code, result = analytics.calc_metrics(data, 1)

    assert code == analytics.ERROR_CODE_OK
    assert result == {
        "avg": 200,
        "total": 600,
        "count": 3
    }


def test_calc_metrics_daily_with_category_filter():
    """Daily metrics include only the selected category."""
    data = [
        {"amount": 100, "cat": "food"},
        {"amount": 200, "cat": "electronics"},
        {"amount": 300, "cat": "food"}
    ]

    code, result = analytics.calc_metrics(data, 1, "food")

    assert code == analytics.ERROR_CODE_OK
    assert result == {
        "avg": 200,
        "total": 400,
        "count": 2
    }


def test_calc_metrics_daily_no_matching_category():
    """No matching category returns NO_DATA."""
    data = [
        {"amount": 100, "cat": "food"}
    ]

    code, result = analytics.calc_metrics(data, 1, "electronics")

    assert code == analytics.ERROR_CODE_NO_DATA
    assert result is None


def test_calc_metrics_weekly():
    """Weekly metrics group records by week."""
    data = [
        {"amount": 100, "week": 1},
        {"amount": 200, "week": 1},
        {"amount": 300, "week": 2}
    ]

    code, result = analytics.calc_metrics(data, 2)

    assert code == analytics.ERROR_CODE_OK
    assert result["total_weeks"] == 2
    assert result["weeks"][1] == {
        "total": 300,
        "count": 2,
        "avg": 150
    }
    assert result["weeks"][2] == {
        "total": 300,
        "count": 1,
        "avg": 300
    }


def test_calc_metrics_monthly():
    """Monthly metrics group records by month."""
    data = [
        {"amount": 100, "month": 1},
        {"amount": 300, "month": 1},
        {"amount": 200, "month": 2}
    ]

    code, result = analytics.calc_metrics(data, 3)

    assert code == analytics.ERROR_CODE_OK
    assert result["total_months"] == 2
    assert result["months"][1]["total"] == 400
    assert result["months"][1]["avg"] == 200


def test_calc_metrics_yearly():
    """Yearly metrics group records by year."""
    data = [
        {"amount": 100, "year": 2025},
        {"amount": 300, "year": 2025},
        {"amount": 200, "year": 2026}
    ]

    code, result = analytics.calc_metrics(data, 4)

    assert code == analytics.ERROR_CODE_OK
    assert result["years"][2025] == {
        "total": 400,
        "count": 2,
        "avg": 200
    }
    assert result["years"][2026]["total"] == 200


def test_calc_metrics_cache_mode():
    """Cache mode stores calculated metrics."""
    data = [{"amount": 100}]

    code, result = analytics.calc_metrics(
        data, 1, m="cache"
    )

    assert code == analytics.ERROR_CODE_OK
    assert analytics.GLOBAL_CACHE["1_None"] == result


def test_calc_metrics_unknown_type():
    """Unknown metric type returns an empty result."""
    data = [{"amount": 100}]

    code, result = analytics.calc_metrics(data, 99)

    assert code == analytics.ERROR_CODE_OK
    assert result == {}


# 2. get_top_products

def test_get_top_products_by_revenue():
    """Products are sorted by revenue in descending order."""
    data = [
        {"product_id": 1, "product_name": "A",
         "amount": 100, "qty": 2},
        {"product_id": 2, "product_name": "B",
         "amount": 300, "qty": 1},
        {"product_id": 3, "product_name": "C",
         "amount": 200, "qty": 3}
    ]

    result = analytics.get_top_products(data)

    assert [item["id"] for item in result] == [2, 3, 1]


def test_get_top_products_limit():
    """Only the requested number of products is returned."""
    data = [
        {"product_id": 1, "amount": 100},
        {"product_id": 2, "amount": 300},
        {"product_id": 3, "amount": 200}
    ]

    result = analytics.get_top_products(data, n=2)

    assert len(result) == 2
    assert result[0]["id"] == 2


def test_get_top_products_by_units():
    """Products can be sorted by units sold."""
    data = [
        {"product_id": 1, "amount": 100, "qty": 2},
        {"product_id": 2, "amount": 50, "qty": 10},
        {"product_id": 3, "amount": 200, "qty": 5}
    ]

    result = analytics.get_top_products(data, sort_by="units")

    assert [item["id"] for item in result] == [2, 3, 1]


def test_get_top_products_empty_data():
    """Empty input returns an empty list."""
    assert analytics.get_top_products([]) == []


def test_get_top_products_aggregates_same_product():
    """Sales of the same product are aggregated."""
    data = [
        {"product_id": 1, "product_name": "Phone",
         "amount": 100, "qty": 2},
        {"product_id": 1, "product_name": "Phone",
         "amount": 200, "qty": 3}
    ]

    result = analytics.get_top_products(data)

    assert len(result) == 1
    assert result[0]["revenue"] == 300
    assert result[0]["units"] == 5
    assert result[0]["orders"] == 2


# 3. calculate_growth and duplicate functions

@pytest.mark.parametrize(
    "function",
    [
        analytics.calculate_growth,
        analytics.calculate_growth_yoy,
        analytics.calculate_growth_mom,
        analytics.calculate_growth_wow
    ]
)
def test_growth_positive(function):
    """All growth functions calculate positive growth."""
    assert function(150, 100) == 50.0


@pytest.mark.parametrize(
    "function",
    [
        analytics.calculate_growth,
        analytics.calculate_growth_yoy,
        analytics.calculate_growth_mom,
        analytics.calculate_growth_wow
    ]
)
def test_growth_negative(function):
    """All growth functions calculate negative growth."""
    assert function(80, 100) == -20.0


@pytest.mark.parametrize(
    "function",
    [
        analytics.calculate_growth,
        analytics.calculate_growth_yoy,
        analytics.calculate_growth_mom,
        analytics.calculate_growth_wow
    ]
)
def test_growth_zero_previous(function):
    """Growth returns 100 when previous value is zero
    and current value is positive."""
    assert function(100, 0) == 100.0


@pytest.mark.parametrize(
    "function",
    [
        analytics.calculate_growth,
        analytics.calculate_growth_yoy,
        analytics.calculate_growth_mom,
        analytics.calculate_growth_wow
    ]
)
def test_growth_both_values_zero(function):
    """Growth returns zero when both values are zero."""
    assert function(0, 0) == 0.0


# 4. Additional analytical functions

def test_get_conversion_rate():
    """Conversion rate is calculated as a percentage."""
    assert analytics.get_conversion_rate(200, 20) == 10.0


def test_get_conversion_rate_zero_visitors():
    """Zero visitors return zero conversion rate."""
    assert analytics.get_conversion_rate(0, 10) == 0


def test_get_avg_order_value():
    """Average order value is calculated correctly."""
    assert analytics.get_avg_order_value(1000, 10) == 100.0


def test_get_avg_order_value_zero_orders():
    """Zero orders return zero average order value."""
    assert analytics.get_avg_order_value(1000, 0) == 0


def test_get_revenue_per_visitor():
    """Revenue per visitor is calculated correctly."""
    assert analytics.get_revenue_per_visitor(1000, 200) == 5.0


def test_get_revenue_per_visitor_zero_visitors():
    """Zero visitors return zero revenue per visitor."""
    assert analytics.get_revenue_per_visitor(1000, 0) == 0


# 5. Global state and reset_stats

def test_reset_stats_clears_statistics_and_cache():
    """Reset clears counters and cached values."""
    analytics.GLOBAL_STATS["calls"] = 5
    analytics.GLOBAL_STATS["errors"] = 2
    analytics.GLOBAL_CACHE["test"] = {"total": 100}

    analytics.reset_stats()

    assert analytics.GLOBAL_STATS == {
        "calls": 0,
        "errors": 0,
        "last_reset": None
    }
    assert analytics.GLOBAL_CACHE == {}


def test_calc_metrics_increments_call_counter():
    """Each call increments the global calls counter."""
    data = [{"amount": 100}]

    analytics.calc_metrics(data, 1)
    analytics.calc_metrics(data, 1)

    assert analytics.GLOBAL_STATS["calls"] == 2


# 6. generate_dashboard

def test_generate_dashboard_no_orders(monkeypatch):
    """Dashboard returns an error when there are no orders."""

    def mock_get_data(name):
        return [] if name == "orders" else []

    monkeypatch.setattr("src.db.get_data", mock_get_data)

    result = analytics.generate_dashboard()

    assert result == {
        "error": "no data",
        "code": analytics.ERROR_CODE_NO_DATA
    }


def test_generate_dashboard_daily(monkeypatch):
    """Dashboard calculates financial and user metrics."""

    orders = [
        {
            "id": 1,
            "product_id": 1,
            "product_name": "Laptop",
            "amount": 1000,
            "qty": 1,
            "status": "paid"
        },
        {
            "id": 2,
            "product_id": 2,
            "product_name": "Mouse",
            "amount": 200,
            "qty": 2,
            "status": "paid"
        },
        {
            "id": 3,
            "product_id": 1,
            "product_name": "Laptop",
            "amount": 500,
            "qty": 1,
            "status": "refunded"
        }
    ]

    users = [
        {"id": 1, "role": 3},
        {"id": 2, "role": 2},
        {"id": 3, "role": 1}
    ]

    products = []

    def mock_get_data(name):
        data = {
            "orders": orders,
            "users": users,
            "products": products
        }
        return data[name]

    def mock_proc():
        return {}

    monkeypatch.setattr("src.db.get_data", mock_get_data)
    monkeypatch.setattr("src.process.proc", mock_proc)

    result = analytics.generate_dashboard()

    assert result["period"] == "daily"
    assert result["total_revenue"] == 1200
    assert result["total_orders"] == 2
    assert result["total_tax"] == 240
    assert result["refunded"] == 500
    assert result["net_revenue"] == 460

    assert result["users"] == {
        "premium": 1,
        "regular": 1,
        "other": 1,
        "total": 3
    }

    assert result["metrics"]["total"] == 1700
    assert result["metrics"]["count"] == 3


def test_generate_dashboard_weekly(monkeypatch):
    """Weekly dashboard uses weekly metrics."""

    orders = [
        {"amount": 100, "week": 1, "status": "paid"},
        {"amount": 200, "week": 2, "status": "paid"}
    ]

    def mock_get_data(name):
        if name == "orders":
            return orders
        return []

    monkeypatch.setattr("src.db.get_data", mock_get_data)
    monkeypatch.setattr("src.process.proc", lambda: {})

    result = analytics.generate_dashboard(period="weekly")

    assert result["period"] == "weekly"
    assert "weeks" in result["metrics"]
    assert result["metrics"]["total_weeks"] == 2


def test_generate_dashboard_calls_proc(monkeypatch):
    """Dashboard invokes the processing function."""

    orders = [{"amount": 100, "status": "paid"}]
    calls = {"count": 0}

    def mock_get_data(name):
        return orders if name == "orders" else []

    def mock_proc():
        calls["count"] += 1
        return {}

    monkeypatch.setattr("src.db.get_data", mock_get_data)
    monkeypatch.setattr("src.process.proc", mock_proc)

    analytics.generate_dashboard()

    assert calls["count"] == 1
