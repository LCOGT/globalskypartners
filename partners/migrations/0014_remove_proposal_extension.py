# Generated by Django 3.1.5 on 2021-03-25 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0013_auto_20210324_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='extension',
        ),
    ]
