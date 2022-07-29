# Generated by Django 3.2.3 on 2022-07-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_auto_20211102_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imprint',
            name='demographic',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Under-served or under-represented'), (1, 'Developing world'), (2, 'Well served communities'), (3, 'Mixed representation'), (99, 'Other')], verbose_name='audience demographic'),
        ),
    ]
