# Generated by Django 3.1.5 on 2021-02-18 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0006_auto_20210129_1033'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cohort',
            options={'ordering': ('year',)},
        ),
        migrations.AlterModelOptions(
            name='semester',
            options={'ordering': ('start',)},
        ),
    ]
