import datetime

from django.conf import settings

__all__ = ("ORDER_DAYEND",)

ORDER_DAYEND = getattr(settings, "ORDER_DAYEND", datetime.time(23, 59, 59, 999))
"""Day end; After this time, the created order would set order date to
tomorrow.
"""


assert isinstance(
    ORDER_DAYEND, datetime.time
), f"Expected time object for ORDER_DAYEND, got {type(ORDER_DAYEND).__name__}"
