# Generated by Django 4.2.4 on 2023-09-26 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0024_alter_blogpost_recent_activity_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
