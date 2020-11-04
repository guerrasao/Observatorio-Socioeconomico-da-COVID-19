
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import AbrangenciaForm, ContinenteForm
from django.contrib.auth.decorators import login_required
from .forms import ImportarTabelaForm
from .processing.xlsx import importar_xlsx, importar_municipios_rs_xlsx

# Create your views here.
@login_required
def importar_dados(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar_xlsx(request.FILES['tabela'])
            return HttpResponseRedirect('/dados/importar')
    else:
        form = ImportarTabelaForm()
    return render(request, 'dados/importar.html', {'form': form})

@login_required
def importar_municipios_rs(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar_municipios_rs_xlsx(request.FILES['tabela'])
            return HttpResponseRedirect('/dados/importar_municipios_rs')
    else:
        form = ImportarTabelaForm()
    return render(request, 'dados/importar.html', {'form': form})