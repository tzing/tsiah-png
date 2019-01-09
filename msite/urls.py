"""Tsiah-Png URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import uuid

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from django.views.decorators.cache import cache_page

stage_id = uuid.uuid4()  # workaround for translation version

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tsiahpng.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('api/', include('api.urls', namespace='api')),

    # i18n
    path(
        'jsi18n/',
        cache_page(86400, key_prefix=f'jsi18n-{stage_id.hex}')(
            JavaScriptCatalog.as_view(packages=[
                'tsiahpng',
                'account',
            ])),
        name='javascript-catalog',
    ),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
