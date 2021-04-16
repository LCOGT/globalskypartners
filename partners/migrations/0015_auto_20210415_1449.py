# Generated by Django 3.1.5 on 2021-04-15 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partners', '0014_remove_proposal_extension'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='pi_email',
        ),
        migrations.RemoveField(
            model_name='partner',
            name='submitter',
        ),
        migrations.AddField(
            model_name='proposal',
            name='submitter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='partner',
            name='pi',
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='partners.partner')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='partner',
            name='pi',
            field=models.ManyToManyField(blank=True, through='partners.Membership', to=settings.AUTH_USER_MODEL),
        ),
    ]
