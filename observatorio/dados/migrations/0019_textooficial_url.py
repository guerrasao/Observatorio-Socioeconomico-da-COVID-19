# Generated by Django 3.1.1 on 2020-12-02 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0018_textooficial'),
    ]

    operations = [
        migrations.AddField(
            model_name='textooficial',
            name='url',
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]
