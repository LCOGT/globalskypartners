# Generated by Django 3.2.18 on 2023-05-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0022_auto_20220715_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='code',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
