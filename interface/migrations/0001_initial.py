# Generated by Django 5.1.7 on 2025-04-20 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutMe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='Bio')),
                ('profile_img', models.ImageField(blank=True, null=True, upload_to='profile_images/', verbose_name='Profile Image')),
                ('background_img', models.ImageField(blank=True, null=True, upload_to='background_images/', verbose_name='Background Image')),
                ('skills', models.TextField(blank=True, null=True, verbose_name='Skills')),
            ],
        ),
    ]
