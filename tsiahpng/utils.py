import datetime
import hashlib

from django.conf import settings
from django.utils import timezone

from django.contrib import messages


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


def str2bool(txt):
    """Convert string to bool, use for query parameter
    """
    if not bool(txt):
        return False
    return str(txt).lower() in ('1', 'y', 'yes', 't', 'true')


def get_messages(request):
    storage = messages.get_messages(request)
    success = list(filter(lambda m: m.level == messages.SUCCESS, storage))
    error = list(filter(lambda m: m.level == messages.ERROR, storage))
    return {'success_messages': success, 'error_messages': error}


def is_new_post(request):
    """A utility to test if the post is duplicated sent, or really the new one.

    Return
    ------
    is_valid : bool
        True if this request is valid.
    """
    post_content = request.POST.urlencode().encode('utf-8')
    hash_str = hashlib.sha1(post_content).hexdigest()
    if request.session.get(f'{request.path}/last_post') == hash_str:
        return False
    request.session[f'{request.path}/last_post'] = hash_str
    return True
