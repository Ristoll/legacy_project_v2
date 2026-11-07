from typing import Any, Dict
from src.analytics_models import _ANALYTICS_STATE, ErrorCode, MetricType, _ANALYTICS_STATE, DEFAULT_TAX_RATE

def _calc_daily_metrics(
    data: list[Dict[str, Any]],
    category: str = None
) -> Dict[str, Any] | None:
    """Calculate average, total and count for daily metrics."""
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


def _group_by_period(
    data: list[Dict[str, Any]],
    field: str,
    result_key: str,
    total_key: str = None
) -> Dict[str, Any]:
    """Group records by period and calculate totals, counts, and averages."""
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

def calc_metrics(data: list[Dict[str, Any]], type: MetricType, filter: str = None, mode: str = None) -> tuple[ErrorCode, Dict[str, Any] | None]:
    """Calculate metrics for the specified period and mode."""
    _ANALYTICS_STATE.record_call()

    if not data:
        _ANALYTICS_STATE.record_error()
        return ErrorCode.NO_DATA, None

    if type == MetricType.DAILY:
        result = _calc_daily_metrics(data, filter)

        if result is None:
            return ErrorCode.NO_DATA, None

    else:
        period_config = {
            MetricType.WEEKLY: ("week", "weeks", "total_weeks"),
            MetricType.MONTHLY: ("month", "months", "total_months"),
            MetricType.YEARLY: ("year", "years", None),
        }

        config = period_config.get(type)

        if config:
            field, result_key, total_key = config
            result = _group_by_period(data, field, result_key, total_key)
        else:
            result = {}

    if mode == "cache":
        cache_key = str(type) + "_" + str(filter)
        _ANALYTICS_STATE.cache[cache_key] = result

    return ErrorCode.OK, result

def reset_stats():
    """reset global statistics - should be called daily"""
    _ANALYTICS_STATE.reset()