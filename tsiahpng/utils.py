__all__ = ("try_parse",)


def try_parse(value, default=0, type=int):
    """Try to parse the input value into certian type. Return default on error.
    """
    try:
        return type(value)
    except (TypeError, ValueError):
        return default
