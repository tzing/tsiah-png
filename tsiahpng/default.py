from datetime import timedelta

from django.utils import timezone

from . import settings


def default_order_date():
    """Get the default date for `order_date`.

    It returns today as default, but would change to tomorrow if current
    time exceeds the time `TSIAHPNG_DAYEND` in settings.
    """
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    if current_time >= settings.ORDER_DAYEND:
        return today + timedelta(days=1)
    else:
        return today
