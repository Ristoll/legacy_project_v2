# analytics.py
# Sales analytics and metrics calculation
# Created: 2020-11-02.
# Refactored by: Chamata Kristina, 2026-11-07
# analytics.py
# Sales analytics and metrics calculation
# Created: 2020-11-02.
# Refactored by: Chamata Kristina, 2026-11-07

from src.analytics_models import (
    ErrorCode,
    MetricType,
    UserRole,
    AnalyticsStats,
    _ANALYTICS_STATE,
    PERCENTAGE_MULTIPLIER,
    INITIAL_GROWTH_BASELINE,
    DEFAULT_TAX_RATE,
)

from src.analytics_metrics import (
    _calc_daily_metrics,
    _group_by_period,
    calc_metrics,
    reset_stats,
)

from src.analytics_growth import (
    calculate_growth,
    calculate_growth_yoy,
    calculate_growth_mom,
    calculate_growth_wow,
    get_conversion_rate,
    get_avg_order_value,
    get_revenue_per_visitor,
)

from src.analytics_products import get_top_products

from src.analytics_dashboard import (
    _summarize_orders,
    _segment_users,
    generate_dashboard,
)