# Generated by Django 3.2.16 on 2025-02-26 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20250226_1541'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created_at',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
