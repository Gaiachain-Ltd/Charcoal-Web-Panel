# Generated by Django 2.2.7 on 2020-07-10 15:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entities', '0010_package_is_finished'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_name', models.CharField(max_length=12, verbose_name='Action name')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='entities.Package', verbose_name='Package')),
                ('read_by', models.ManyToManyField(related_name='read_notifications', to=settings.AUTH_USER_MODEL, verbose_name='Read by', blank=True)),
                ('users', models.ManyToManyField(related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Users')),
            ],
        ),
    ]
