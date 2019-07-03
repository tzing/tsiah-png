from django.conf import settings


__all__ = ("ACCOUNT_PER_PAGE",)


ITEMS_PER_PAGE = getattr(settings, "ITEMS_PER_PAGE", 24)
"""Number of items to be displayed in a single page.
"""

PASSBOOK_PER_PAGE = getattr(settings, "PASSBOOK_PER_PAGE", ITEMS_PER_PAGE)
"""[int] Specific number of passbooks to be displayed in a single page, or it
would use ``ITEMS_PER_PAGE``.
"""

TRANSACTION_PER_PAGE = getattr(settings, "TRANSACTION_PER_PAGE", 50)
"""[int] Number of transactions to be displayed in a single page.
"""

ALLOW_ANYONE_ALTER_TRANSACTION = getattr(
    settings, "ALLOW_ANYONE_ALTER_TRANSACTION", True
)
"""[bool] Let anyone create transaction.
"""


def _assert_type(name, type_):
    value = globals()[name]
    assert isinstance(
        value, type_
    ), f"Expected {type_.__name__} for {name}, got {type(value).__name__}"


_assert_type("ITEMS_PER_PAGE", int)
_assert_type("PASSBOOK_PER_PAGE", int)
_assert_type("TRANSACTION_PER_PAGE", int)
_assert_type("ALLOW_ANYONE_ALTER_TRANSACTION", bool)
