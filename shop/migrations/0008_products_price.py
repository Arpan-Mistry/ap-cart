# Generated by Django 3.2 on 2021-05-31 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_orderupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
