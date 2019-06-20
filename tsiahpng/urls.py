import uuid

from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from . import views
from . import admin

app_name = "tsiahpng"

caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path("", views.homepage, name="welcome"),
    # menu
    path("menu/", views.shop_list, name="shop_list"),
    path("menu/<int:shop_id>/", views.shop_detail, name="shop_detail"),
    path("menu/<int:shop_id>/add", views.shop_add_product, name="shop_add_product"),
    # order
    path("order/", views.order_list, name="order_list"),
    path("order/new/", views.order_create, name="order_create"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("order/<int:order_id>/close", views.order_close, name="order_close"),
    path(
        "order/<int:order_id>/stringify", views.order_stringify, name="order_stringify"
    ),
    # js i18n
    path("jsi18n/", caches(JavaScriptCatalog.as_view()), name="javascript-catalog"),
    # admin panel
    path("administration/", admin.site.urls, name="admin"),
]
