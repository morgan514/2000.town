# Generated by Django 4.2.4 on 2023-09-02 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0012_alter_blogpost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
