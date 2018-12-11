# 呷飯 Tsia̍h-Pn̄g

Group buying tool to collect the orders from your friends.

**NOTICE** this project is **not** design for production.


## About

*Tsia̍h-Pn̄g* is the word for *eat food* in [Taiwanese Hokkien].
I first created this project because I always collect orders from colleagues.

[Taiwanese Hokkien]: https://en.wikipedia.org/wiki/Taiwanese_Hokkien


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

2. Built database

    ```bash
    python manage.py makemigrations tsiahpng
    python manage.py migrate
    ```

3. (Optional) Build i18n (for Traditional Chinese)

    ```bash
    django-admin compilemessages --use-fuzzy
    ```

4. Create users

    ```bash
    python manage.py createsuperuser
    ```

5. Run!

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

6. If you want to use this site with your friends, follow the instruction from django document:

    https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


## TODO

- [ ] Account: for quickly review the spent money
    - [ ] pay-as-you-go
    - [ ] prepaid
