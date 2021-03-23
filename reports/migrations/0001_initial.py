# Generated by Django 3.1.5 on 2021-02-18 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partners', '0007_auto_20210218_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countries', django_countries.fields.CountryField(max_length=746, multiple=True)),
                ('summary', models.TextField(verbose_name='summary of activity')),
                ('comment', models.TextField(verbose_name='comments')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='partners.partner')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='partners.cohort')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='description of product')),
                ('link', models.URLField(blank=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.report')),
            ],
        ),
        migrations.CreateModel(
            name='Imprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField()),
                ('audience', models.PositiveSmallIntegerField(choices=[(0, 'Elementary school students'), (1, 'High school students'), (2, 'Teachers'), (3, 'Families'), (4, 'General Public'), (5, 'Adult learners')])),
                ('activity', models.PositiveSmallIntegerField(choices=[(0, 'Student workshops'), (1, 'Teacher workshops'), (2, 'School workshops'), (3, 'Online school workshops'), (4, 'Student mentoring'), (5, 'Student research'), (6, 'Beginners tutorials'), (7, 'Citizen Science'), (8, 'Artistic project')], verbose_name='type of activity')),
                ('demographic', models.PositiveSmallIntegerField(choices=[(0, 'Under-served or under-represented'), (1, 'Developing world'), (2, 'Well served communities')], verbose_name='audience demographic')),
                ('demo_other', models.TextField(blank=True, verbose_name='other demographic')),
                ('impact', models.TextField(blank=True, verbose_name='primary impact')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.report')),
            ],
        ),
    ]
