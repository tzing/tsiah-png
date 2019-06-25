import uuid

from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from . import views

app_name = "account"

caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path("", views.account_list, name="list"),
    path("<int:passbook_id>/", views.account_detail, name="detail"),
    path("<int:passbook_id>/add", views.create_event, name="create_event"),
    path("from-order/<int:order_id>", views.order_close, name="order_close"),
    path("api/accounts", views.account_list_api, name="api-list"),
    path("jsi18n/", caches(JavaScriptCatalog.as_view()), name="javascript-catalog"),
]
