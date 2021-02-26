# Generated by Django 3.1.5 on 2021-02-22 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0024_noticiaexterna_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grafico',
            name='abrangencia',
            field=models.CharField(choices=[('CONT', 'Continente'), ('PAIS', 'País'), ('ESTA', 'Estado'), ('ESRS', 'Estado do RS'), ('MUNI', 'Município')], max_length=4),
        ),
        migrations.AlterField(
            model_name='grafico',
            name='tipo',
            field=models.CharField(blank=True, choices=[('LINH', 'Linhas')], default='LINH', max_length=4),
        ),
    ]