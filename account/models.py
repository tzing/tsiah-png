from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _


class Passbook(models.Model):
    """Passbook saves all the transactions.
    """

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=_("Passbook name"), max_length=256, unique=True
    )

    ordering = models.IntegerField(
        verbose_name=_("Ordering"), default=-1, db_index=True
    )

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Unselect this instead of deleting passbook."),
    )

    changeable = models.BooleanField(
        verbose_name=_("Changeable"),
        default=True,
        help_text=_("Unchecked if users are not allowed to make changes."),
    )

    note = models.TextField(
        verbose_name=_("Note"),
        null=True,
        blank=True,
        help_text=_(
            "You can warp text by *stars* to <em>emphasize</em> it, **double stars** to make it <strong>bolder</strong> and ~~tilde~~ to <strike>delete</strike> it."
        ),
    )

    class Meta:
        verbose_name = _("Passbook")
        verbose_name_plural = _("Passbooks")

        ordering = ["-ordering"]

    def save(self, *args, **kwargs):
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def events(self, **kwargs):
        return Event.objects.filter(book=self, **kwargs)

    def balance(self):
        events = self.events()
        transactions = Transaction.objects.filter(event__in=events)
        balance = transactions.aggregate(val=models.Sum("balance"))["val"]
        return balance or 0

    balance.short_description = _("Balance")


class Event(models.Model):
    """Events are collection to transactions.

    Since this program is a group-buying tool, there would be multiple users
    involved in a single order or event. This class is a collection to real
    transactions.
    """

    id = models.AutoField(primary_key=True)

    book = models.ForeignKey(
        verbose_name=_("Passbook"), to=Passbook, on_delete=models.CASCADE, db_index=True
    )

    date_created = models.DateTimeField(
        verbose_name=_("Date created"), auto_now_add=True
    )

    title = models.CharField(
        verbose_name=_("Title"), max_length=256, blank=True, null=True
    )

    related_order = models.ForeignKey(
        verbose_name=_("Related order"),
        to="tsiahpng.Order",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True,
    )

    subtotal = models.FloatField(verbose_name=_("Subtotal"))

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

        ordering = ["-date_created"]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = None
        if not self.related_order:
            self.related_order = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.title:
            return self.title
        return _("Record created on {create:%Y/%m/%d %H:%M}").format(
            create=localtime(self.date_created)
        )

    def transactions(self, **kwargs):
        return Transaction.objects.filter(event=self, **kwargs)


class Transaction(models.Model):
    """The real transaction record
    """

    id = models.AutoField(primary_key=True)

    event = models.ForeignKey(
        verbose_name=_("Event"), to=Event, on_delete=models.CASCADE, db_index=True
    )

    user = models.ForeignKey(
        verbose_name=_("User"),
        to="auth.User",
        on_delete=models.CASCADE,
        null=True,
        db_index=True,
    )

    balance = models.FloatField(verbose_name=_("Change in balance"))

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

        unique_together = ("event", "user")

    def __str__(self):
        return _("[{event}] {user} ${balance:+,}").format(
            event=self.event, user=self.user, balance=self.balance
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        parent = self.event
        parent.subtotal = parent.transactions().aggregate(val=models.Sum("balance"))[
            "val"
        ]
        parent.save()
