# Generated by Django 3.1.1 on 2020-11-03 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0011_auto_20201021_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estado',
            name='codigo_ibge',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]