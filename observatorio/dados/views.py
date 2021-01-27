
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .forms import AbrangenciaForm, ContinenteForm
from django.contrib.auth.decorators import login_required
from .forms import ImportarTabelaForm
from .processing.xlsx import importar_xlsx, importar_municipios_rs_xlsx
from django.db.models import Sum
from .models import Variavel, VariavelMunicipioInteiro, VariavelMunicipioDecimal, NoticiaExterna

# Create your views here.
@login_required
def importar_dados(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar_xlsx(request.FILES['tabela'])
            return HttpResponseRedirect('importar_dados')
    else:
        form = ImportarTabelaForm()
    return render(request, 'dados/importar_dados.html', {'form': form})

@login_required
def importar_municipios_rs(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar_municipios_rs_xlsx(request.FILES['tabela'])
            return HttpResponseRedirect('importar_municipios_rs')
    else:
        form = ImportarTabelaForm()
    return render(request, 'dados/importar_municipios_rs.html', {'form': form})

### Index ###
def get_latest_news_criacao(count=3):
    return NoticiaExterna.objects.filter(tipo='CRIA')

def get_latest_news_opiniao(count=3):
    return NoticiaExterna.objects.filter(tipo='NOTI')

def get_latest_news_live(count=3):
    return NoticiaExterna.objects.filter(tipo='LIVE')

def index(request):
    return render(request, 'dados/index.html', 
    {
        'latest_news_criacao': get_latest_news_criacao(),
        'latest_news_opiniao': get_latest_news_opiniao,
        'latest_news_live': get_latest_news_live
    })

def pagina_inicial(request):
    return HttpResponseRedirect('pagina-inicial/')

### End Index ###

### Dados ###
def dados(request):
    return render(request, 'dados/dados.html')

### End Dados ###

def rank_municipios_por_variavel(request, estado, variavel):
    variavel_atual = get_object_or_404(Variavel, id=variavel)
    
    result = []
    #result = Books.objects.values('author').order_by('author').annotate(total_price=Sum('price'))
    #users = User.objects.filter(is_active=True)
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'result': result}
    )