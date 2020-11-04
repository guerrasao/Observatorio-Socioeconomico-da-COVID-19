from django import forms
from .models import Variavel, Continente

class AbrangenciaForm(forms.Form):
    abrangencia = forms.ChoiceField(choices=Variavel.ABRANGENCIA_VARIAVEL)

class ContinenteForm(forms.Form):
    continente = forms.ModelChoiceField(queryset=Continente.objects.all())

class ImportarTabelaForm(forms.Form):
    tabela = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',}))