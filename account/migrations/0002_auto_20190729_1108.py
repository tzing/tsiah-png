# Generated by Django 2.2.3 on 2019-07-29 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='balance',
            field=models.FloatField(verbose_name='Change in balance'),
        ),
    ]
