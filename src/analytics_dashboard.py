from typing import Dict, Any

from src.analytics_metrics import calc_metrics
from src.analytics_models import _ANALYTICS_STATE, DEFAULT_TAX_RATE, ErrorCode, MetricType, UserRole
from src.analytics_products import get_top_products


def _summarize_orders(orders: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate total revenue, taxes, paid orders, and refunds."""
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

def _segment_users(users: list[Dict[str, Any]]) -> Dict[str, Any]:
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

def generate_dashboard(period="daily", category=None):
    """Generate a dashboard with aggregated order and user statistics."""
    from src.db import get_data
    from src.process import proc

    proc()

    orders = get_data("orders")
    users = get_data("users")

    if not orders:
        return {"error": "no data", "code": ErrorCode.NO_DATA}

    order_summary = _summarize_orders(orders)
    user_segments = _segment_users(users)

    top_prods = get_top_products(orders)

    _, metrics = calc_metrics(
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