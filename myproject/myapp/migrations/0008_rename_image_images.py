# Generated by Django 4.2 on 2024-07-15 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_rename_imagein_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='Images',
        ),
    ]
