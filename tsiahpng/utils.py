import hashlib

from django.contrib import auth

__all__ = ("try_parse", "str2bool", "get_username")


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
    return str(txt).lower() in ("1", "y", "yes", "t", "true")


def get_username(user):
    name = user.get_full_name().strip()
    if not name:
        name = user.get_username().strip()
    return name


def get_stuff_ordering(request):
    """Query stuffs for ordering form.
    """
    return {
        "users": auth.models.User.objects.filter(is_active=True),
        "last_user": request.session.get("ordering/last_user"),
    }


def is_new_post(request):
    """A utility to test if the post is duplicated sent, or really the new one.

    Return
    ------
    is_valid : bool
        True if this request is valid.
    """
    post_content = request.POST.urlencode().encode("utf-8")
    hash_str = hashlib.sha1(post_content).hexdigest()
    if request.session.get(f"{request.path}/last_post") == hash_str:
        return False
    request.session[f"{request.path}/last_post"] = hash_str
    return True
