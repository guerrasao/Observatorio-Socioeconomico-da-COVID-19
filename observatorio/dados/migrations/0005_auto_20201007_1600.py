# Generated by Django 3.1.1 on 2020-10-07 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0004_auto_20201007_1525'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrdemVariaveisGrafico',
            new_name='VariaveisGrafico',
        ),
        migrations.AlterModelOptions(
            name='variaveisgrafico',
            options={'verbose_name': 'Variáveis do Gráfico'},
        ),
    ]