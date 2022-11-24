# Generated by Django 3.2.13 on 2022-08-21 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbmodel', '0002_alter_crowdinfo_shoot_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='warning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warn_type', models.CharField(max_length=100)),
                ('camera_id', models.IntegerField()),
                ('warn_time', models.DateTimeField(auto_now_add=True)),
                ('info', models.CharField(max_length=500, null=True)),
            ],
        ),
    ]
