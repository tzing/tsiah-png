from django.db import migrations, models


def set_default(apps, schema_editor):
    Event = apps.get_model("account", "Event")
    Transaction = apps.get_model("account", "Transaction")

    for event in Event.objects.all().iterator():
        event.subtotal = (
            Transaction.objects.filter(event=event).aggregate(
                val=models.Sum("balance")
            )["val"]
            or 0
        )
        event.save()


class Migration(migrations.Migration):

    dependencies = [("account", "0002_auto_20190729_1108")]

    operations = [
        migrations.AddField(
            model_name="event",
            name="subtotal",
            field=models.FloatField(null=True, verbose_name="Subtotal"),
            preserve_default=False,
        ),
        migrations.RunPython(set_default),
        migrations.AlterField(
            model_name="event",
            name="subtotal",
            field=models.FloatField(verbose_name="Subtotal"),
            preserve_default=True,
        ),
    ]
