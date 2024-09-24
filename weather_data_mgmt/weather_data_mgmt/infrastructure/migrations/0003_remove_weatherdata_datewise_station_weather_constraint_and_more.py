# Generated by Django 5.1.1 on 2024-09-21 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0002_remove_weatherdata_datewise_state_weather_constraint_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='weatherdata',
            name='datewise station weather constraint',
        ),
        migrations.AddConstraint(
            model_name='weatherdata',
            constraint=models.UniqueConstraint(fields=('state', 'station', 'date'), name='datewise station weather constraint'),
        ),
    ]
