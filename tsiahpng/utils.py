def try_get(request, field, w_type=int, default=0):
    value_raw = request.POST.get(field)
    if value_raw is None:
        return default
    try:
        return w_type(value_raw)
    except (TypeError, ValueError):
        return default
