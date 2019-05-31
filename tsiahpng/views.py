import uuid

from django.shortcuts import render
from django.urls import path

from django.views.i18n import JavaScriptCatalog
from django.views.decorators.cache import cache_page

from . import admin

app_name = "tsiahpng"
caches = cache_page(86400, key_prefix=f"jsi18n-{uuid.uuid4().hex}")

urlpatterns = [
    path(
        "jsi18n/",
        caches(JavaScriptCatalog.as_view(packages=["tsiahpng"])),
        name="javascript-catalog",
    ),
    path("administration/", admin.site.urls, name="admin"),
]
