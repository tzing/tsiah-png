from django import forms

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
            print(self.errors)
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
