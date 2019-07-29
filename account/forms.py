from django import forms
from django.http import QueryDict
from django.contrib import auth

import tsiahpng.forms

from . import models


class AddEventForm(forms.Form):
    passbook = forms.IntegerField()
    title = forms.CharField(max_length=128, required=False)
    order = forms.IntegerField(min_value=1, required=False)
    users = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            param = next(filter(lambda p: isinstance(p, QueryDict), args))
        except StopIteration:
            return

        # dynamic add fields
        user_ids = param.get("users").split(",")
        for id_ in user_ids:
            self.fields[f"balance_{id_}"] = forms.FloatField()

    def to_model(self) -> models.Event:
        if not self.is_valid():
            return None

        # get passbook
        try:
            passbook = models.Passbook.objects.get(
                id=self.cleaned_data["passbook"], is_active=True, changeable=True
            )
        except models.Passbook.DoesNotExist:
            return None

        # get users
        user_ids = set()
        for id_ in self.cleaned_data["users"].split(","):
            try:
                user_ids.add(int(id_))
            except (TypeError, ValueError):
                ...
        users = auth.models.User.objects.filter(id__in=user_ids, is_active=True)

        if not users:
            return None

        # get order
        order = None
        if self.cleaned_data["order"] is not None:
            try:
                order = tsiahpng.models.Order.objects.get(
                    id=self.cleaned_data["order"], is_active=True
                )
            except tsiahpng.models.Order.DoesNotExist:
                ...

        # create event
        event = models.Event.objects.create(
            title=self.cleaned_data["title"].strip(), book=passbook, related_order=order
        )

        # create transaction
        for user in users:
            balance = self.cleaned_data[f"balance_{user.id}"]
            if balance == 0:
                continue

            models.Transaction.objects.create(event=event, user=user, balance=balance)

        return event
