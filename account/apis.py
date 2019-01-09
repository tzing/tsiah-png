from django.http import JsonResponse

from tsiahpng import utils

from . import models


def query_passbooks(request):
    """Return name of all passbooks

    Query Parameters
    ----------------
        sui (default: False)
            return the result in semantic ui format
    """
    # parse parameters
    use_sui = utils.str2bool(request.GET.get('sui'))

    # query
    passbooks = models.Passbook.objects.filter(is_active=True)

    # make context
    context = {}
    for passbook in passbooks:
        context[passbook.id] = str(passbook)

    # return
    if not use_sui:
        return JsonResponse(context)
    else:
        return JsonResponse({
            'success':
            True,
            'results': [{
                'name': name,
                'value': uid,
            } for uid, name in context.items()]
        })
