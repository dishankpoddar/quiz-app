# Generated by Django 3.0.5 on 2020-07-01 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20200630_0856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_student',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_teacher',
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('AD', 'Admin'), ('TE', 'Teacher'), ('ST', 'Student')], default='UD', max_length=2),
        ),
    ]
