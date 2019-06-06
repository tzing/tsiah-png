import collections
import random
import uuid

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import path, include

from django.contrib import messages

from django.utils.translation import gettext as _

from django.views.i18n import JavaScriptCatalog
from django.views.decorators.cache import cache_page

from . import admin
from . import default
from . import forms
from . import models
from . import settings
from . import utils


def homepage(request):
    context = {"messages": messages.get_messages(request)}

    # welcome string
    if models.WelcomeText.objects.exists():
        welcome = random.choice(models.WelcomeText.objects.filter(is_active=True))
        context.update(title=welcome.title, subtitle=welcome.subtitle)
    else:
        context.update(title=_("Welcome"), subtitle=None)

    return render(request, "tsiahpng/homepage.pug", context)


def shop_list(request):
    shops = models.Shop.objects.filter(is_active=True)

    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(shops, settings.SHOP_PER_PAGE)

    return render(
        request,
        "tsiahpng/menu/index.pug",
        {
            "title": _("Menu"),
            "shops": paginator.get_page(idx_page),
            "messages": messages.get_messages(request),
        },
    )


def shop_detail(request, shop_id):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id, is_active=True)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop #{id} not exists.").format(id=shop_id))
        return redirect("tsiahpng:shop_list")

    # organize products
    sorted_products = collections.OrderedDict()
    for category in shop.related_categories():
        sorted_products[category] = shop.products(category=category)

    unsorted_products = shop.products(category=None)
    if unsorted_products:
        sorted_products[None] = unsorted_products

    # available orders
    orders = models.Order.objects.filter(shop=shop, is_active=True, is_available=True)

    return render(
        request,
        "tsiahpng/menu/detail.pug",
        {
            "title": str(shop),
            "shop": shop,
            "messages": messages.get_messages(request),
            "related_products": sorted_products,
            "available_orders": orders,
        },
    )


def shop_add_product(request, shop_id):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id, is_active=True)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop #{id} not exists.").format(id=shop_id))
        return redirect("tsiahpng:shop_list")

    # check permission
    if not shop.changeable:
        messages.error(request, _("{shop} is not changeable.").format(shop=shop))
        return redirect("tsiahpng:shop_detail", shop_id=shop_id)

    # form
    if request.method == "POST":
        form = forms.CreateProductForm(request.POST)
        prod = form.to_model()
        if prod:
            messages.success(request, _(f"Successfully add {prod}.").format(prod=prod))
            request.session[f"shop_add_product/{shop.id}/price"] = prod.price
            request.session[f"shop_add_product/{shop.id}/category"] = prod.category.id
            return redirect("tsiahpng:shop_detail", shop_id=shop_id)
        else:
            messages.error(request, _("Invalid requests."))

    # render
    return render(
        request,
        "tsiahpng/menu/add_product.pug",
        {
            "title": _("Add product to {shop}").format(shop=shop),
            "shop": shop,
            "categories": models.Category.objects.all(),
            "default_product_price": request.session.get(
                f"shop_add_product/{shop.id}/price", settings.DEFAULT_PROD_PRICE
            ),
            "last_category": request.session.get(
                f"shop_add_product/{shop.id}/category", -1
            ),
            "messages": messages.get_messages(request),
        },
    )


def order_list(request):
    orders = models.Order.objects.filter(is_active=True)

    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(orders, settings.ORDER_PER_PAGE)

    return render(
        request,
        "tsiahpng/order/index.pug",
        {
            "title": _("Order"),
            "orders": paginator.get_page(idx_page),
            "messages": messages.get_messages(request),
        },
    )


def order_detail(request, order_id):
    # get order
    try:
        order = models.Order.objects.get(id=order_id, is_active=True)
    except models.Order.DoesNotExist:
        messages.error(request, _("Order #{id} id not exists.").format(id=order_id))
        return redirect("tsiahpng:order_list")

    return render(
        request, "tsiahpng/order/detail.pug", {"title": str(order), "order": order}
    )


def order_create(request):
    # post request
    if request.method == "POST":
        form = forms.CreateOrderForm(request.POST)
        order = form.to_model()
        if order:
            messages.success(
                request, _(f'Successfully create order "{order}".').format(order=order)
            )
            request.session["order_create/last_shop"] = order.shop.id
            return redirect("tsiahpng:order_list")  # FIXME link
        else:
            messages.error(request, _("Invalid requests."))

    # shops
    shops = models.Shop.objects.filter(is_active=True)

    return render(
        request,
        "tsiahpng/order/create_order.pug",
        {
            "title": _("Create order"),
            "shops": shops,
            "default_date": default.default_order_date(),
            "last_shop": request.session.get("order_create/last_shop"),
            "messages": messages.get_messages(request),
        },
    )


# url confs
app_name = "tsiahpng"
caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path("", homepage, name="welcome"),
    # menu
    path("menu/", shop_list, name="shop_list"),
    path("menu/<int:shop_id>/", shop_detail, name="shop_detail"),
    path("menu/<int:shop_id>/add", shop_add_product, name="shop_add_product"),
    # order
    path("order/", order_list, name="order_list"),
    path("order/new/", order_create, name="order_create"),
    path("order/<int:order_id>/", order_detail, name="order_detail"),
    # API
    path("api/", include("tsiahpng.apis", namespace="api")),
    # js i18n
    path("jsi18n/", caches(JavaScriptCatalog.as_view()), name="javascript-catalog"),
    # admin panel
    path("administration/", admin.site.urls, name="admin"),
]
