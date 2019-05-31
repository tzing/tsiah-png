import random
import uuid

from django.shortcuts import render, redirect
from django.urls import path

from django.contrib import messages

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


def shop_detail(request):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop not exists."))
        return redirect("tsiahpng:welcome")

    raise NotImplementedError()  # FIXME


def shop_add_product(request, shop_id):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop not exists."))
        return redirect("tsiahpng:welcome")

    # check permission
    if not shop.changeable:
        messages.error(request, _("{shop} is not changeable.").format(shop=shop))
        return redirect("tsiahpng:shop_detail", shop_id=shop_id)

    raise NotImplementedError()  # FIXME

    # render
    return render(
        request,
        "tsiahpng/menu/add_product.pug",
        {"title": _("Add product to {shop}".format(shop=shop))},
    )


# url confs
app_name = "tsiahpng"
caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path("", homepage, name="welcome"),
    # menu
    path("menu/", shop_list, name="shop_list"),
    path("menu/<int:shop_id>", shop_detail, name="shop_detail"),
    path("menu/<int:shop_id>/add", shop_add_product, name="shop_add_product"),
    # js i18n
    path(
        "jsi18n/",
        caches(JavaScriptCatalog.as_view(packages=["tsiahpng"])),
        name="javascript-catalog",
    ),
    # admin panel
    path("administration/", admin.site.urls, name="admin"),
]
