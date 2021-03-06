# Generated by Django 2.2.2 on 2019-07-02 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tsiahpng', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Passbook',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Passbook name')),
                ('ordering', models.IntegerField(db_index=True, default=-1, verbose_name='Ordering')),
                ('is_active', models.BooleanField(default=True, help_text='Unselect this instead of deleting passbook.', verbose_name='Active')),
                ('changeable', models.BooleanField(default=True, help_text='Unchecked if users are not allowed to make changes.', verbose_name='Changeable')),
                ('note', models.TextField(blank=True, help_text='You can warp text by *stars* to <em>emphasize</em> it, **double stars** to make it <strong>bolder</strong> and ~~tilde~~ to <strike>delete</strike> it.', null=True, verbose_name='Note')),
            ],
            options={
                'verbose_name': 'Passbook',
                'verbose_name_plural': 'Passbooks',
                'ordering': ['-ordering'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('title', models.CharField(blank=True, max_length=256, null=True, verbose_name='Title')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Passbook', verbose_name='Passbook')),
                ('related_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tsiahpng.Order', verbose_name='Related order')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('balance', models.IntegerField(verbose_name='Change in balance')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Event', verbose_name='Event')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'unique_together': {('event', 'user')},
            },
        ),
    ]
