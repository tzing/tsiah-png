from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import django.contrib.auth.models

import tsiahpng.models


class Passbook(models.Model):
    """A passbook that saves all the transactions inside.
    """
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=_('Passbook name'),
        max_length=256,
        unique=True,
    )

    priority = models.IntegerField(
        verbose_name=_('Priority'),
        default=0,
        db_index=True,
    )

    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    note = models.TextField(verbose_name=_('Note'), null=True, blank=True)

    class Meta:
        verbose_name = _('Passbook')
        verbose_name_plural = _('Passbooks')

        ordering = ['-priority']

    def save(self, *args, **kwargs):
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def events(self, **kwargs):
        return Event.objects.filter(book=self, **kwargs)

    def balance(self):
        transactions = Transaction.objects.filter(event__in=self.events())
        balance = transactions.aggregate(val=models.Sum('balance'))['val']
        if balance is None:
            return 0
        else:
            return balance

    def peruser_balance(self):
        """Returns per-user balances
        """
        transactions = Transaction.objects.filter(event__in=self.events())
        user_ids = transactions.values_list('user')

        distinct_ids = user_ids.order_by().distinct()
        users = django.contrib.auth.models.User.objects.filter(
            id__in=distinct_ids)

        per_user_balance = []
        for user in users:
            r_transaction = transactions.filter(user=user)
            balance = r_transaction.aggregate(val=models.Sum('balance'))['val']
            per_user_balance.append((user, balance))

        return per_user_balance


class Event(models.Model):
    """An event that trigger transactions. Since this is a group-buying tool,
    there would be multiple users involved in a single order or event. This
    class is a collection to the real transaction.
    """
    id = models.AutoField(primary_key=True)

    book = models.ForeignKey(
        verbose_name=_('Passbook'),
        to=Passbook,
        on_delete=models.CASCADE,
        db_index=True)

    creation = models.DateTimeField(
        verbose_name=_('Creation time'),
        default=timezone.localtime,
    )

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=256,
        blank=True,
        null=True,
    )

    related_order = models.ForeignKey(
        verbose_name=_('Related order'),
        to=tsiahpng.models.Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

        ordering = ['-creation']

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = None
        if not self.related_order:
            self.related_order = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.title:
            return self.title
        return f'{self.creation} {self.book}'

    def transactions(self, **kwargs):
        return Transaction.objects.filter(event=self, **kwargs)

    def balance(self):
        balance = self.transactions().aggregate(
            val=models.Sum('balance'))['val']
        if balance is None:
            return 0
        else:
            return balance


class Transaction(models.Model):
    """The real transaction record
    """
    id = models.AutoField(primary_key=True)

    event = models.ForeignKey(
        verbose_name=_('Event'),
        to=Event,
        on_delete=models.CASCADE,
        db_index=True,
    )

    user = models.ForeignKey(
        verbose_name=_('User'),
        to=django.contrib.auth.models.User,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )

    balance = models.IntegerField(verbose_name=_('Change in balance'))

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

        unique_together = ('event', 'user')

    def __str__(self):
        return f'[{self.event}] {self.user} ${self.balance:+,}'
