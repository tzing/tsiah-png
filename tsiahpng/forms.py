import typing

from django import forms
from django.http import QueryDict
from django.contrib import auth

from django.utils.translation import gettext as _

from . import models
from . import settings

__all__ = ("CreateProductForm", "CreateOrderForm")


class CreateProductForm(forms.Form):
    shop = forms.IntegerField()
    category = forms.IntegerField()
    name = forms.CharField(max_length=128)
    price = forms.IntegerField()

    def to_model(self) -> models.Product:
        """Convert form data to model, or return None if any error happens.
        """
        if not self.is_valid():
            return None

        try:
            shop = models.Shop.objects.get(
                id=self.cleaned_data["shop"], is_active=True, changeable=True
            )
        except models.Shop.DoesNotExist:
            return None

        if self.cleaned_data["category"] == -1:
            category = None
        else:
            try:
                category = models.Category.objects.get(id=self.cleaned_data["category"])
            except models.Category.DoesNotExist:
                return None

        return models.Product.objects.create(
            shop=shop,
            category=category,
            name=self.cleaned_data["name"],
            price=self.cleaned_data["price"],
        )


class CreateOrderForm(forms.Form):
    shop = forms.IntegerField()
    name = forms.CharField(max_length=128, required=False)
    date = forms.DateField(input_formats=["%Y/%m/%d", "%Y-%m-%d"])
    note = forms.CharField(required=False)

    def to_model(self) -> models.Order:
        if not self.is_valid():
            return None

        try:
            shop = models.Shop.objects.get(id=self.cleaned_data["shop"], is_active=True)
        except models.Shop.DoesNotExist:
            return None

        return models.Order.objects.create(
            alias=self.cleaned_data["name"],
            shop=shop,
            order_date=self.cleaned_data["date"],
            note=self.cleaned_data["note"],
        )


class OrderingForm(forms.Form):
    order = forms.IntegerField()
    user = forms.IntegerField()
    items = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            param = next(filter(lambda p: isinstance(p, QueryDict), args))
        except StopIteration:
            return

        # dynamic add fields
        item_ids = param.get("items").split(",")
        for id_ in item_ids:
            self.fields[f"quantity_{id_}"] = forms.IntegerField(min_value=0)
            self.fields[f"price_{id_}"] = forms.IntegerField(min_value=0)
            self.fields[f"note_{id_}"] = forms.CharField(max_length=768, required=False)

    def to_models(self) -> typing.List[models.Ticket]:
        if not self.is_valid():
            return None

        # get user
        try:
            user = auth.models.User.objects.get(
                id=self.cleaned_data["user"], is_active=True
            )
        except auth.models.User.DoesNotExist:
            return []

        # get order object
        try:
            order = models.Order.objects.get(
                id=self.cleaned_data["order"], is_active=True, is_available=True
            )
        except models.Order.DoesNotExist:
            return []

        # get ordered products
        product_ids = set()
        for id_ in self.cleaned_data["items"].split(","):
            try:
                product_ids.add(int(id_))
            except (TypeError, ValueError):
                ...
        products = models.Product.objects.filter(id__in=product_ids)

        # build tickets
        tickets = []
        for item in products:
            quantity = self.cleaned_data[f"quantity_{item.id}"]
            if quantity == 0:
                continue

            ticket = models.Ticket.objects.create(
                order=order,
                user=user,
                item=item,
                quantity=quantity,
                cost=self.cleaned_data[f"price_{item.id}"],
                note=self.cleaned_data[f"note_{item.id}"],
            )

            tickets.append(ticket)

        return tickets
