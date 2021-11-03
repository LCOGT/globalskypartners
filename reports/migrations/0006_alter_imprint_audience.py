# Generated by Django 3.2.3 on 2021-11-02 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_imprint_countries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imprint',
            name='audience',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Elementary school students'), (1, 'High school students'), (2, 'Teachers'), (3, 'Families'), (4, 'General Public'), (5, 'Adult learners'), (6, 'Undergraduates'), (7, 'Postgraduates')]),
        ),
    ]