# Generated by Django 5.2 on 2025-04-17 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_parent_child_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='parent',
            name='role',
            field=models.CharField(choices=[('parent', 'Parent'), ('admin', 'Admin'), ('staff', 'Daycare Staff')], default='parent', max_length=10),
        ),
    ]
