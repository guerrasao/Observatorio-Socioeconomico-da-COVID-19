# Generated by Django 3.1.1 on 2020-10-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0008_auto_20201021_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='variavelcontinentedecimal',
            name='valora',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AddField(
            model_name='variavelcontinenteinteiro',
            name='valora',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='variavelestadodecimal',
            name='valora',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AddField(
            model_name='variavelestadointeiro',
            name='valora',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='variavelmunicipiodecimal',
            name='valora',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AddField(
            model_name='variavelmunicipiointeiro',
            name='valora',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='variavelpaisdecimal',
            name='valora',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AddField(
            model_name='variavelpaisinteiro',
            name='valora',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
