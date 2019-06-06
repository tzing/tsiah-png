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
