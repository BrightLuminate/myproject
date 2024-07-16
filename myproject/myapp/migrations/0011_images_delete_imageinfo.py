# Generated by Django 4.2 on 2024-07-16 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_delete_surves'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Detection_Time', models.DateTimeField(auto_now_add=True)),
                ('image_name', models.CharField(max_length=255)),
                ('coustomer', models.TextField(max_length=255)),
                ('image_url', models.URLField()),
            ],
        ),
        migrations.DeleteModel(
            name='ImageInfo',
        ),
    ]
