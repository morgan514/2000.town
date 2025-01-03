# Generated by Django 4.2.4 on 2023-09-02 00:26

from django.db import migrations
import image_optimizer.fields


class Migration(migrations.Migration):

    dependencies = [
        ('townapp', '0011_alter_blogpost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='image',
            field=image_optimizer.fields.OptimizedImageField(blank=True, upload_to=''),
        ),
    ]
