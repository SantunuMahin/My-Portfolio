from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')],
                    default='todo',
                    max_length=20,
                )),
                ('priority', models.CharField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                    default='medium',
                    max_length=10,
                )),
                ('due_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
