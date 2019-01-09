# 呷飯 Tsia̍h-Pn̄g

A group buying tool for collecting orders (especially the meal/drink orders) from your friends.

*Tsia̍h-Pn̄g* is the word for *eat food* in [Taiwanese Hokkien].
I first created this project because I always collect breakfast orders from colleagues.

[Taiwanese Hokkien]: https://en.wikipedia.org/wiki/Taiwanese_Hokkien


## Usage

Basically, you can run and use it *if you are on local network*.

- About user

    It use django built-in `User` models for the *users* in the dropdown.
    Use django admin to create users and make changes.

- About menu

    `Shop` and `Category` could only be created by admin.
    `Product` could be created by anyone, because I am lazy and I don't want to copy the entire menu form shops.

- About django admin

    Directly go to *http://HOSTNAME/admin/* by url.
    There is no place to link to the admin panel from the site


## Prerequisites

- python >= 3.6
- [django](https://www.djangoproject.com/)
- [Pillow](https://pillow.readthedocs.io/en/latest/)


## Install

0. Clone this repo & get submodules

    ```bash
    git clone git@github.com:tzing/tsiah-png.git --recursive
    cd tsiah-png
    ```

1. Get dependency

    ```bash
    pipenv install
    ```

    *- or -*

    ```bash
    pip install django Pillow
    ```

2. Set secret key

    ```bash
    export SECRET_KEY="SOMETHING_RANDOM_ENOUGH"
    ```

    *WARNING* Keep this value secret. See [django docs](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY) for more info.

3. Built database

    ```bash
    python manage.py makemigrations tsiahpng account
    python manage.py migrate
    ```

4. (Optional) Build i18n (for Traditional Chinese)

    ```bash
    django-admin compilemessages --use-fuzzy
    ```

5. Create users

    ```bash
    python manage.py createsuperuser
    ```

6. Run!

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

7. If you want to use this site on the Internet, follow the instruction from django document:

    https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


## Credits

Icons made by [Freepik](https://www.freepik.com/) from [www.flaticon.com](https://www.flaticon.com/) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/).


## TODO

- [ ] layout
    - [x] menu detail: too many category
    - [ ] order list: too many order
- [ ] Deploy guide


## Minor Feature

### Summary String

You can copy the summary string from the order review page, for quickly send
the order to the shop via instant message app.

It requires the prebuilt `SummaryTemplate` to provides the template on built
the summary string.
Rather than starts from nothing, you can use the command to create the minimal
one and modify it.

```bash
python manage.py createtemplate <NAME_TO_TEMPLATE>
```

Use `-h` option to see more info.
