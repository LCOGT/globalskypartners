# Generated by Django 3.1.5 on 2021-05-17 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0017_auto_20210517_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='emailed',
            field=models.DateTimeField(blank=True),
        ),
    ]