from django import forms
from .models import Variavel, Continente, VariavelMunicipioInteiro, VariavelEstadoInteiro

class AbrangenciaForm(forms.Form):
    abrangencia = forms.ChoiceField(choices=Variavel.ABRANGENCIA_VARIAVEL)

class ContinenteForm(forms.Form):
    continente = forms.ModelChoiceField(queryset=Continente.objects.all())

class ImportarTabelaForm(forms.Form):
    tabela = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',}))

class RankingVarMuni(forms.Form):
    EXTRA_CHOICES = [
        ('Todos', 'Todos'),
    ]
    variavel = forms.ModelChoiceField(label="Variável", queryset=Variavel.objects.filter(abrangencia='MUNI', ativa=True), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Variável'}))
    periodo = forms.ChoiceField(label="Período/Ano", initial=('Todos','Todos'), choices=(), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Periodo/Ano' }))
    
    def __init__(self, *args, **kwargs):
        super(RankingVarMuni, self).__init__(*args, **kwargs)
        choices = [(ano['data__year'], ano['data__year']) for ano in VariavelMunicipioInteiro.objects.values('data__year').order_by('data__year').distinct()]
        choices.extend(self.EXTRA_CHOICES)
        self.fields['periodo'].choices = choices

class RankingVarEsta(forms.Form):
    EXTRA_CHOICES = [
        ('Todos', 'Todos'),
    ]
    variavel = forms.ModelChoiceField(label="Variável", queryset=Variavel.objects.filter(abrangencia='ESTA', variavel_exclusiva_do_estado_RS=False, ativa=True), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Variável'}))
    periodo = forms.ChoiceField(label="Período/Ano", initial=('Todos','Todos'), choices=(), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Periodo/Ano' }))
    
    def __init__(self, *args, **kwargs):
        super(RankingVarEsta, self).__init__(*args, **kwargs)
        choices = [(ano['data__year'], ano['data__year']) for ano in VariavelEstadoInteiro.objects.values('data__year').order_by('data__year').distinct()]
        choices.extend(self.EXTRA_CHOICES)
        self.fields['periodo'].choices = choices

class RankingVarEstaMensal(forms.Form):
    variavel = forms.ModelChoiceField(label="Variável", queryset=Variavel.objects.filter(abrangencia='ESTA', variavel_exclusiva_do_estado_RS=False, ativa=True), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Variável'}))
    periodo = forms.ChoiceField(label="Período (Mês/Ano)", choices=(), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Periodo (Mês/Ano)' }))
    
    def __init__(self, *args, **kwargs):
        super(RankingVarEstaMensal, self).__init__(*args, **kwargs)
        choices = [(ano['data'], str(ano['data__month'])+'/'+str(ano['data__year'])) for ano in VariavelEstadoInteiro.objects.exclude(valor__isnull=True).values('data','data__month','data__year').order_by('-data').distinct()]
        self.fields['periodo'].choices = choices

class RankingVarMuniMensal(forms.Form):
    variavel = forms.ModelChoiceField(label="Variável", queryset=Variavel.objects.filter(abrangencia='MUNI', ativa=True), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Variável'}))
    periodo = forms.ChoiceField(label="Período (Mês/Ano)", choices=(), widget=forms.Select(attrs={'class':'form-select form-control', 'aria-label':'Periodo (Mês/Ano)' }))
    
    def __init__(self, *args, **kwargs):
        super(RankingVarMuniMensal, self).__init__(*args, **kwargs)
        choices = [(ano['data'], str(ano['data__month'])+'/'+str(ano['data__year'])) for ano in VariavelMunicipioInteiro.objects.exclude(valor__isnull=True).values('data','data__month','data__year').order_by('-data').distinct()]
        self.fields['periodo'].choices = choices