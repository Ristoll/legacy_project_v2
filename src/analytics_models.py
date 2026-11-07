"""Analytics models, enums, constants and shared state."""
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
        """Record an analytics function call."""
        self.stats["calls"] += 1

    def record_error(self) -> None:
        """Record an analytics error."""
        self.stats["errors"] += 1

    def reset(self) -> None:
        """Reset execution statistics and clear the cache."""
        self.stats.update({ "calls": 0, "errors": 0, "last_reset": None, })
        self.cache.clear()

_ANALYTICS_STATE = AnalyticsStats()
PERCENTAGE_MULTIPLIER = 100.0
INITIAL_GROWTH_BASELINE = 100.0
DEFAULT_TAX_RATE = 0.2
