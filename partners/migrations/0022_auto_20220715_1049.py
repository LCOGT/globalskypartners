# Generated by Django 3.2.3 on 2022-07-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0021_cohort_active_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohort',
            name='call_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='ID of call in obs portal'),
        ),
        migrations.AlterField(
            model_name='review',
            name='verdict',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Verdict Pending'), (0, 'Rejected'), (1, 'Accepted'), (2, 'Further Questions')], default=3),
        ),
    ]
