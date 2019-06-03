from django import forms

from django.utils.translation import gettext as _

from . import models
from . import settings


class CreateProductForm(forms.Form):
    shop = forms.IntegerField(widget=forms.HiddenInput())
    category = forms.IntegerField()
    name = forms.CharField(label=_("Product name"), max_length=128)
    price = forms.IntegerField(label=_("Price"), initial=settings.DEFAULT_PROD_PRICE)

    def to_model(self) -> models.Product:
        """Convert form data to model, or return None if any error happens.
        """
        try:
            shop = models.Shop.objects.get(id=self.cleaned_data["shop"])
        except models.Category.DoesNotExist:
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
