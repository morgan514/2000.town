# Generated by Django 4.2.4 on 2024-10-08 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0035_alter_theme_custom_font'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='custom_font',
            field=models.FileField(blank=True, null=True, upload_to='fonts/'),
        ),
    ]
