import datetime

from django.conf import settings

__all__ = ("ORDER_DAYEND", "DEFAULT_PROD_PRICE", "SHOP_PER_PAGE")

ORDER_DAYEND = getattr(settings, "ORDER_DAYEND", datetime.time(23, 59, 59, 999))
"""[datetime.time] Day end; After this time, the created order would set order
date to tomorrow.
"""

DEFAULT_PROD_PRICE = getattr(settings, "DEFAULT_PROD_PRICE", 30)
"""[int] Default price of products.
"""

SHOP_PER_PAGE = getattr(settings, "SHOP_PER_PAGE", 25)
"""Number of shops to be displayed in the same page.
"""


def _assert_type(name, type_):
    value = globals()[name]
    assert isinstance(
        value, type_
    ), f"Expected {type_.__name__} for {name}, got {type(value).__name__}"


_assert_type("ORDER_DAYEND", datetime.time)
_assert_type("DEFAULT_PROD_PRICE", int)
_assert_type("SHOP_PER_PAGE", int)
