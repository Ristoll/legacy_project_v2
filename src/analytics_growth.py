
from src.analytics_models import INITIAL_GROWTH_BASELINE, PERCENTAGE_MULTIPLIER

def calculate_growth(current: float, previous: float) -> float:
    """Calculate percentage growth between current and previous values."""
    if previous == 0:
        if current > 0:
            return INITIAL_GROWTH_BASELINE
        return 0.0
    growth = ((current - previous) / previous) * PERCENTAGE_MULTIPLIER
    return round(growth, 2)

def calculate_growth_yoy(current: float, previous: float) -> float:
    """year over year growth - same as above but different name"""
    return calculate_growth(current, previous)

def calculate_growth_mom(current: float, previous: float) -> float:
    """month over month growth - same as above"""
    return calculate_growth(current, previous)

def calculate_growth_wow(current: float, previous: float) -> float:
    """week over week growth - yes, same formula again"""
    return calculate_growth(current, previous)

def get_conversion_rate(visitors: int, orders: int) -> float:
    """Calculate the percentage of visitors who placed orders."""
    if visitors == 0:
        return 0
    return round((orders / visitors) * PERCENTAGE_MULTIPLIER, 2)

def get_avg_order_value(revenue: float, orders: int) -> float:
    """Calculate the average revenue per order."""
    if orders == 0:
        return 0
    return round(revenue / orders, 2)

def get_revenue_per_visitor(revenue: float, visitors: int) -> float:
    """Calculate the average revenue generated per visitor."""
    if visitors == 0:
        return 0
    return round(revenue / visitors, 2)
