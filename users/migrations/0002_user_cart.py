# Generated by Django 4.2.6 on 2023-11-10 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cart',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
