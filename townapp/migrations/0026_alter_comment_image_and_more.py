# Generated by Django 4.2.4 on 2023-09-26 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0025_alter_blogpost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
