from django.http import JsonResponse
from django.urls import path

from django.contrib import auth

from . import models
from . import utils


def get_users(request):
    if utils.str2bool(request.GET.get("all")):
        users = auth.models.User.objects.all()
    else:
        users = auth.models.User.objects.filter(is_active=True)

    results = []
    for user in users:
        results.append({"name": utils.get_username(user), "value": user.id})

    return JsonResponse({"success": True, "results": results})


# url configuration
app_name = "api"

urlpatterns = [path("users/", get_users, name="user")]
