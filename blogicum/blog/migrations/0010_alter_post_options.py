# Generated by Django 3.2.16 on 2025-03-22 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_alter_post_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created_at',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
