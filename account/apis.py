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
    use_sui = utils.str2bool(request.GET.get('sui'))

    passbooks = models.Passbook.objects.filter(is_active=True)

    if use_sui:
        context = [{'name': str(p), 'value': p.id} for p in passbooks]
        return JsonResponse({'success': True, 'results': context})
    else:
        context = dict((p.id, str(p)) for p in passbooks)
        return JsonResponse(context)
