# Generated by Django 3.1.5 on 2021-01-21 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='program',
            field=models.ManyToManyField(blank=True, to='partners.ProgramType'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='region',
            field=models.ManyToManyField(blank=True, to='partners.Region'),
        ),
    ]
