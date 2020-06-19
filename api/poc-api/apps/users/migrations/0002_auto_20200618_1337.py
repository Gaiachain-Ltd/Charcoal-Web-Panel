# Generated by Django 2.2.7 on 2020-06-18 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='code',
            field=models.CharField(blank=True, max_length=8, verbose_name='Code'),
        ),
        migrations.AddField(
            model_name='user',
            name='contact',
            field=models.CharField(blank=True, max_length=16, verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='user',
            name='function',
            field=models.CharField(blank=True, choices=[('AD', 'President Malebi'), ('KP', 'Vice President'), ('PM', "Malebi's Rep - Accountant"), ('NA', 'Carbonizer')], max_length=2, verbose_name='Function'),
        ),
    ]