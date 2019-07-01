# Installation

There are two components in this project -- main part and `account` plugin.
Accounting plugin is disabled by default and would not affect other features.


## Table of Contents
<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [ Table of Contents](#table-of-contents)
- [ Prerequisites](#prerequisites)
- [ Clone](#clone)
- [ Install dependencies](#install-dependencies)
- [ Create Django project](#create-django-project)
- [ Install Tsia̍h-Pn̄g](#install-tsia̍h-pn̄g)
  - [ Register apps](#register-apps)
  - [ Configure URL](#configure-url)
  - [ Setup Pug](#setup-pug)
  - [ Setup SASS processor](#setup-sass-processor)
- [ Optional settings](#optional-settings)
  - [ Media file path & url](#media-file-path-url)
  - [ Internationlization](#internationlization)
  - [ Error views](#error-views)
  - [ Change admin site](#change-admin-site)
- [ Enable accounting plugin](#enable-accounting-plugin)

<!-- /code_chunk_output -->

## Prerequisites

- python >= 3.6
- [pipenv](https://github.com/pypa/pipenv)


## Clone

This project use [Semantic UI], which is imported as git submodule.

```bash
# recursive clone
git clone git@github.com:tzing/tsiah-png.git --recursive --depth=1

# or if you have already cloned
cd tsiah-png
git submodule update --init
```

[Semantic UI]: https://semantic-ui.com/


## Install dependencies

All requirements are listed in [Pipfile](../Pipfile).

```bash
pipenv install --dev
```


## Create Django project

This project is a standalone Django app and there is no Django project file inside repo.

You can use the exists project on your own, or start a empty django project:

```bash
django-admin startproject mysite
```


## Install Tsia̍h-Pn̄g


### Register apps

add three lines in `settings.py`

```py
INSTALLED_APPS = [
    ...
    "tsiahpng.apps.TsiahpngConfig",
    "django.contrib.humanize",
    "sass_processor",
]
```

Please note that `humanize` and `sass_processor` are dependencies.


### Configure URL

Add `path` in `urls.py`, please do *not* change its namespace.

```py
from django.urls import path, include

urlpatterns = [
    ...
    path("", include("tsiahpng.urls", namespace="tsiahpng")),
]
```

Noted `include` is not imported by default.


### Setup Pug

This project use [pug](https://pugjs.org/api/getting-started.html) instead of standard HTML as template.
Therefore, there are more things to set up.

Change the `TEMPLATES` in `settings.py`:

```py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        # disable APP_DIRS
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            # pypugjs part
            "loaders": [
                (
                    "pypugjs.ext.django.Loader",
                    (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ),
                )
            ],
            "builtins": ["pypugjs.ext.django.templatetags"],
        },
    }
]
```


### Setup SASS processor

Still, it use SASS instead of CSS.

Add `STATICFILES_FINDERS` and `STATIC_ROOT` in `settings.py`:

```py
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

STATIC_ROOT = os.path.join(BASE_DIR, "collected_statics")
```


## Optional settings


### Media file path & url

The `ImageField` is used to save menu images. If you want to use it, it is better to setup path and urls.

in `settings.py`:
```py
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

in `urls.py`:
```py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Internationlization

Only Traditional Chinese translation is provided. Or you can [make one] for your language.

與其說只有中文翻譯，不如果只有英文翻譯😂

在 `settings.py` 新增一個 `LocaleMiddleware`，注意它需要晚於 `SessionMiddleware` 且早於 `CommonMiddleware`。

並以`LANGUAGES`取代`LANGUAGE_CODE`。

```py
from django.utils.translation import gettext_lazy as _

MIDDLEWARE = [
   'django.contrib.sessions.middleware.SessionMiddleware',
   'django.middleware.locale.LocaleMiddleware',
   'django.middleware.common.CommonMiddleware',
]

LANGUAGES = [
    ("zh-hant", _("Traditional Chinese")),
    ("en", _("English"))
]
```

[make one]: https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#localization-how-to-create-language-files


### Error views

404 and 500 error views is provided. However, they would [never be displayed] if `DEBUG` is set to `True`.

To use the provided error view, add these lines in the bottom of `urls.py`:
```py
handler404 = "tsiahpng.views.error_404"
handler500 = "tsiahpng.views.error_500"
```

[never be displayed]: https://docs.djangoproject.com/en/2.2/ref/views/#error-views


### Change admin site

It still uses Django admin site, the only difference is that custom site sorts the models based on their relationship.

To use the custom admin site, change the import declaration in `urls.py`:
```py
# from django.contrib import admin
from tsiahpng import admin
```

## Enable accounting plugin

There is only two steps to enable accounting feature.

register `account` in `settings.py`:

```py
INSTALLED_APPS = [
    ...
    "account.apps.AccountConfig", # before tsiah-png
    "tsiahpng.apps.TsiahpngConfig",
    ...
]
```

add url path in `urls.py` (orders doesn't matter):
```py
urlpatterns = [
    path("", include("tsiahpng.urls", namespace="tsiahpng")),
    path("account/", include("account.urls", namespace="tsiahpng-account")),
]
```
