# Generated by Django 3.1.5 on 2021-02-03 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0002_add_songs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='id',
        ),
        migrations.AlterField(
            model_name='history',
            name='Timestamp',
            field=models.DateTimeField(primary_key=True, serialize=False, verbose_name='timestamp'),
        ),
        migrations.AlterField(
            model_name='song',
            name='Id',
            field=models.TextField(primary_key=True, serialize=False, verbose_name='Id'),
        ),
    ]
