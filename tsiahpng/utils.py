import datetime

from django.conf import settings
from django.utils import timezone


def order_date_default():
    """Get the default date for `order_date`.

    It returns today as default, but would change to tomorrow if current
    time exceeds the time `TSIAHPNG_DAYEND` in settings.
    """
    now = timezone.localtime()

    # get day end setting
    if not hasattr(settings, 'TSIAHPNG_DAYEND'):
        return now.date()

    day_end = getattr(settings, 'TSIAHPNG_DAYEND')
    if not isinstance(day_end, datetime.time):
        return now.date()

    # compare current time to day end
    if now.time() >= day_end:
        return now.date() + datetime.timedelta(days=1)
    else:
        return now.date()


def try_parse(value, default=0, type=int):
    """Try to parse the input value into certian type. Return default on error.
    """
    try:
        return type(value)
    except (TypeError, ValueError):
        return default
