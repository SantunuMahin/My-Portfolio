# Generated by Django 5.1.7 on 2025-04-24 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0002_aboutme_resume'),
    ]

    operations = [
        migrations.CreateModel(
            name='CP_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Title')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Url')),
                ('activity_img', models.ImageField(blank=True, null=True, upload_to='Activity_img/', verbose_name='Activity_img')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Details')),
            ],
        ),
    ]
