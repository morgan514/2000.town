# Generated by Django 4.2.4 on 2023-09-05 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0015_alter_userprofile_options_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
