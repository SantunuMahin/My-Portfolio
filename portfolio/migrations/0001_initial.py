from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('bio', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('company_url', models.URLField(blank=True)),
                ('university', models.CharField(blank=True, max_length=200)),
                ('university_url', models.URLField(blank=True)),
                ('github_url', models.URLField(blank=True)),
                ('linkedin_url', models.URLField(blank=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='profile/')),
                ('cv', models.FileField(blank=True, help_text='Upload your CV (PDF)', null=True, upload_to='cv/')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profile',
            },
        ),
        migrations.CreateModel(
            name='SkillCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='skills/')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Skill Category',
                'verbose_name_plural': 'Skill Categories',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.ImageField(blank=True, null=True, upload_to='services/')),
                ('icon_name', models.CharField(blank=True, help_text='Ionicon name e.g. code-slash-outline', max_length=50)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('web', 'Web Development'), ('ml', 'Machine Learning'), ('mobile', 'Mobile App'), ('data', 'Data Science'), ('other', 'Other')], default='web', max_length=50)),
                ('description', models.TextField()),
                ('tech_stack', models.CharField(blank=True, help_text='e.g. Django, React, PostgreSQL', max_length=300)),
                ('image', models.ImageField(blank=True, null=True, upload_to='projects/')),
                ('github_url', models.URLField(blank=True)),
                ('live_url', models.URLField(blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200)),
                ('company_url', models.URLField(blank=True)),
                ('role', models.CharField(max_length=200)),
                ('start_date', models.CharField(help_text='e.g. January 2023', max_length=50)),
                ('end_date', models.CharField(blank=True, help_text='Leave blank if current', max_length=50)),
                ('is_current', models.BooleanField(default=False)),
                ('description', models.TextField(help_text='Bullet points, one per line')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Experience',
                'verbose_name_plural': 'Experiences',
                'ordering': ['order', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('institution_url', models.URLField(blank=True)),
                ('degree', models.CharField(max_length=200)),
                ('field', models.CharField(blank=True, max_length=200)),
                ('start_date', models.CharField(max_length=50)),
                ('end_date', models.CharField(blank=True, max_length=50)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('details', models.TextField(blank=True, help_text='Additional info, one bullet per line')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Education',
                'verbose_name_plural': 'Education',
                'ordering': ['order', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('level', models.PositiveIntegerField(default=80, help_text='Proficiency 0-100')),
                ('order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='portfolio.skillcategory')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
