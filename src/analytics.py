# analytics.py
# Sales analytics and metrics calculation
# Created: 2020-11-02. Refactored: never.
# "Works fine, don't touch" - previous developer note
from enum import IntEnum
from typing import Any, Dict


class ErrorCode(IntEnum):
    """Return codes for analytics operations."""
    OK = 0
    NO_DATA = -1
    CALC_FAIL = -2
    DB_FAIL = -3


class MetricType(IntEnum):
    """Supported metric aggregate types."""
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4


class UserRole(IntEnum):
    """User privilege roles."""
    REGULAR = 2
    PREMIUM = 3

class AnalyticsStats:
    """Encapsulates execution statistics and cache."""

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}
        self.stats: Dict[str, Any] = {
            "calls": 0,
            "errors": 0,
            "last_reset": None,
        }

    def record_call(self) -> None:
        self.stats["calls"] += 1

    def record_error(self) -> None:
        self.stats["errors"] += 1

    def reset(self) -> None:
        self.stats.update({ "calls": 0, "errors": 0, "last_reset": None, })
        self.cache.clear()

# Аліаси для збереження зворотної сумісності із зовнішнім кодом та тестами
_ANALYTICS_STATE = AnalyticsStats()
GLOBAL_CACHE = _ANALYTICS_STATE.cache
GLOBAL_STATS = _ANALYTICS_STATE.stats

ERROR_CODE_OK = ErrorCode.OK
ERROR_CODE_NO_DATA = ErrorCode.NO_DATA
ERROR_CODE_CALC_FAIL = ErrorCode.CALC_FAIL
ERROR_CODE_DB_FAIL = ErrorCode.DB_FAIL

PERCENTAGE_MULTIPLIER = 100.0
INITIAL_GROWTH_BASELINE = 100.0
DEFAULT_TAX_RATE = 0.2

def _calc_daily_metrics(data, category=None):
    """Calculate metrics for daily data."""
    total = 0
    count = 0

    for item in data:
        if category and item.get("cat") != category:
            continue

        total += item.get("amount", 0)
        count += 1

    if count == 0:
        return None

    return {
        "avg": total / count,
        "total": total,
        "count": count,
    }


def _group_by_period(data, field, result_key, total_key=None):
    """Group metrics by a specified time period."""
    groups = {}

    for item in data:
        period = item.get(field, 0)

        if period not in groups:
            groups[period] = {"total": 0, "count": 0}

        groups[period]["total"] += item.get("amount", 0)
        groups[period]["count"] += 1

    for group in groups.values():
        group["avg"] = group["total"] / group["count"]

    result = {result_key: groups}

    if total_key:
        result[total_key] = len(groups)

    return result


def _summarize_orders(orders):
    """Calculate revenue, order count, tax and refunds."""
    total_revenue = 0
    total_orders = 0
    total_tax = 0
    refunded = 0

    for order in orders:
        if order.get("status") == "paid":
            amount = order.get("amount", 0)
            total_revenue += amount
            total_orders += 1
            total_tax += amount * DEFAULT_TAX_RATE

        elif order.get("status") == "refunded":
            refunded += order.get("amount", 0)

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_tax": total_tax,
        "refunded": refunded,
    }


def _segment_users(users):
    """Count users by role."""
    premium = 0
    regular = 0
    other = 0

    for user in users:
        role = user.get("role")

        if role == UserRole.PREMIUM:
            premium += 1
        elif role == UserRole.REGULAR:
            regular += 1
        else:
            other += 1

    return {
        "premium": premium,
        "regular": regular,
        "other": other,
        "total": len(users),
    }

def calc_metrics(d, t, f=None, m=None):
    """
    Calculate sales metrics.
    d=data, t=type, f=filter, m=mode
    """
    _ANALYTICS_STATE.record_call()

    if not d:
        _ANALYTICS_STATE.record_error()
        return ErrorCode.NO_DATA, None

    if t == MetricType.DAILY:
        r = _calc_daily_metrics(d, f)

        if r is None:
            return ErrorCode.NO_DATA, None

    else:
        period_config = {
            MetricType.WEEKLY: ("week", "weeks", "total_weeks"),
            MetricType.MONTHLY: ("month", "months", "total_months"),
            MetricType.YEARLY: ("year", "years", None),
        }

        config = period_config.get(t)

        if config:
            field, result_key, total_key = config
            r = _group_by_period(d, field, result_key, total_key)
        else:
            r = {}

    if m == "cache":
        cache_key = str(t) + "_" + str(f)
        _ANALYTICS_STATE.cache[cache_key] = r

    return ErrorCode.OK, r

def get_top_products(data, n=10, sort_by="revenue"):
    """get top N products"""
    products = {}
    
    for item in data:
        pid = item.get("product_id")
        if pid not in products:
            products[pid] = {
                "id": pid,
                "name": item.get("product_name", "unknown"),
                "revenue": 0,
                "units": 0,
                "orders": 0
            }
        products[pid]["revenue"] = products[pid]["revenue"] + item.get("amount", 0)
        products[pid]["units"] = products[pid]["units"] + item.get("qty", 0)
        products[pid]["orders"] = products[pid]["orders"] + 1
    
    lst = []
    for pid in products:
        lst.append(products[pid])
    
    # bubble sort instead of sorted()
    for i in range(len(lst)):
        for j in range(len(lst) - 1):
            if lst[j][sort_by] < lst[j+1][sort_by]:
                tmp = lst[j]
                lst[j] = lst[j+1]
                lst[j+1] = tmp
    
    return lst[:n]

def calculate_growth(current, previous):
    """growth rate calculation"""
    if previous == 0:
        if current > 0:
            return INITIAL_GROWTH_BASELINE
        return 0.0
    g = ((current - previous) / previous) * PERCENTAGE_MULTIPLIER
    return round(g, 2)

def calculate_growth_yoy(current, previous):
    """year over year growth - same as above but different name"""
    if previous == 0:
        if current > 0:
            return INITIAL_GROWTH_BASELINE
        return 0.0
    g = ((current - previous) / previous) * PERCENTAGE_MULTIPLIER
    return round(g, 2)

def calculate_growth_mom(current, previous):
    """month over month growth - same as above"""
    if previous == 0:
        if current > 0:
            return INITIAL_GROWTH_BASELINE
        return 0.0
    g = ((current - previous) / previous) * PERCENTAGE_MULTIPLIER
    return round(g, 2)

def calculate_growth_wow(current, previous):
    """week over week growth - yes, same formula again"""
    if previous == 0:
        if current > 0:
            return INITIAL_GROWTH_BASELINE
        return 0.0
    g = ((current - previous) / previous) * PERCENTAGE_MULTIPLIER
    return round(g, 2)

def get_conversion_rate(visitors, orders):
    if visitors == 0:
        return 0
    return round((orders / visitors) * PERCENTAGE_MULTIPLIER, 2)

def get_avg_order_value(revenue, orders):
    if orders == 0:
        return 0
    return round(revenue / orders, 2)

def get_revenue_per_visitor(revenue, visitors):
    if visitors == 0:
        return 0
    return round(revenue / visitors, 2)

def reset_stats():
    """reset global statistics - should be called daily"""
    _ANALYTICS_STATE.reset()

def generate_dashboard(period="daily", category=None):
    """
    Main dashboard function.
    Fetches data from multiple sources and calculates everything.
    """
    from src.db import get_data
    from src.process import proc

    orders = get_data("orders")
    users = get_data("users")
    products = get_data("products")

    if not orders:
        return {"error": "no data", "code": ErrorCode.NO_DATA}

    proc_result = proc()

    order_summary = _summarize_orders(orders)
    user_segments = _segment_users(users)

    top_prods = get_top_products(orders)

    code, metrics = calc_metrics(
        orders,
        MetricType.DAILY if period == "daily" else MetricType.WEEKLY,
        category
    )

    return {
        "period": period,
        "total_revenue": round(order_summary["total_revenue"], 2),
        "total_orders": order_summary["total_orders"],
        "total_tax": round(order_summary["total_tax"], 2),
        "refunded": round(order_summary["refunded"], 2),
        "net_revenue": round(
            order_summary["total_revenue"]
            - order_summary["total_tax"]
            - order_summary["refunded"],
            2
        ),
        "users": user_segments,
        "top_products": top_prods,
        "metrics": metrics,
        "global_stats": _ANALYTICS_STATE.stats.copy()
    }