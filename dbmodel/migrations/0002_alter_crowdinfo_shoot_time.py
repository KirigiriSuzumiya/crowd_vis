# Generated by Django 3.2.13 on 2022-08-18 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmodel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crowdinfo',
            name='shoot_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]