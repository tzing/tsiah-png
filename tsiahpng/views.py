import random
import uuid

from django.shortcuts import render
from django.urls import path

from django.utils.translation import gettext as _

from django.views.i18n import JavaScriptCatalog
from django.views.decorators.cache import cache_page

from . import admin
from . import models


def homepage(request):
    context = {}

    # welcome string
    if models.WelcomeText.objects.exists():
        welcome = random.choice(models.WelcomeText.objects.filter(is_active=True))
        context.update(title=welcome.title, subtitle=welcome.subtitle)
    else:
        context.update(title=_("Welcome"), subtitle=None)

    return render(request, "tsiahpng/homepage.pug", context)


def shop_list(request):
    return render(
        request,
        "tsiahpng/menu/index.pug",
        {"title": _("Menu"), "shops": models.Shop.objects.filter(is_active=True)},
    )


# url confs
app_name = "tsiahpng"
caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path("", homepage, name="welcome"),
    path("menu/", shop_list, name="shop_list"),
    path(
        "jsi18n/",
        caches(JavaScriptCatalog.as_view(packages=["tsiahpng"])),
        name="javascript-catalog",
    ),
    path("administration/", admin.site.urls, name="admin"),
]
