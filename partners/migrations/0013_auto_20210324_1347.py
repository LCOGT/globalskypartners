# Generated by Django 3.1.5 on 2021-03-24 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0012_auto_20210324_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='pi',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='partner',
            name='pi_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
