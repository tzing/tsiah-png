from django.http import JsonResponse

import django.contrib.auth.models

from tsiahpng import utils


def query_users(request):
    """Return all active users

    Query Parameters
    ----------------
        all (default: False)
            return all users, or only active users would be returned
        sui (default: False)
            return the result in semantic ui format
    """
    # parse parameter
    get_all = utils.str2bool(request.GET.get('all'))
    use_sui = utils.str2bool(request.GET.get('sui'))

    # query
    if get_all:
        users = django.contrib.auth.models.User.objects.all()
    else:
        users = django.contrib.auth.models.User.objects.filter(is_active=True)

    # make context
    context = {}
    for user in users:
        name = user.get_full_name()
        if not name.strip():
            name = user.get_username()
        context[user.id] = name

    # return
    if not use_sui:
        return JsonResponse(context)

    return JsonResponse({
        'success':
        True,
        'results': [{
            'name': name,
            'value': uid,
        } for uid, name in context.items()]
    })
