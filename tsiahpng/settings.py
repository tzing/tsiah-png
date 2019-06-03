import datetime

from django.conf import settings

__all__ = ("ORDER_DAYEND",)

ORDER_DAYEND = getattr(settings, "ORDER_DAYEND", datetime.time(23, 59, 59, 999))
"""[datetime.time] Day end; After this time, the created order would set order
date to tomorrow.
"""


DEFAULT_PROD_PRICE = getattr(settings, "DEFAULT_PROD_PRICE", 30)
"""[int] Default price of products.
"""


def assert_type(name, type_):
    value = globals()[name]
    print(value, type_)
    assert isinstance(
        value, type_
    ), f"Expected {type_.__name__} for {name}, got {type(value).__name__}"


assert_type("ORDER_DAYEND", datetime.time)
assert_type("DEFAULT_PROD_PRICE", int)
