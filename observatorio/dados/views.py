from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .forms import AbrangenciaForm, ContinenteForm
from django.contrib.auth.decorators import login_required
from .forms import ImportarTabelaForm
from .processing.xlsx import importar_xlsx, importar_municipios_rs_xlsx
from django.db.models import Sum
from .models import Variavel, VariavelMunicipioInteiro, VariavelMunicipioDecimal, NoticiaExterna, Pais, Grafico, VariavelPais, VariaveisGrafico, VariavelPaisInteiro, VariavelPaisDecimal, Fonte, Estado, Municipio
from django.template.defaultfilters import date as _date
from django.db.models import Max
from copy import deepcopy

# Create your views here.
@login_required
def importar_dados(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            resultado = importar_xlsx(request.FILES['tabela'])
            if(resultado == True):
                return HttpResponseRedirect('importar_dados?sucesso=Dados atualizados com sucesso!')
            else:
                return HttpResponseRedirect('importar_dados?erro='+str(resultado))
    else:
        form = ImportarTabelaForm()
    return render(request, 'dados/importar_dados.html', {'form': form})

@login_required
def importar_municipios_rs(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            resultado = importar_municipios_rs_xlsx(request.FILES['tabela'])
            if(resultado == True):
                return HttpResponseRedirect('importar_municipios_rs?sucesso=Dados atualizados com sucesso!')
            else:
                return HttpResponseRedirect('importar_municipios_rs?erro='+str(resultado))
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

#def pagina_inicial(request):
#    return HttpResponseRedirect('/')

### End Index ###

### Dados ###
def dados(request):
    return render(request, 'dados/dados.html')

### Pais ###
def graficos_pais(request, pais):
    pais = get_object_or_404(Pais, nome_normalizado=pais)
    #print(pais)
    #variaveis = Variavel.objects.filter(tipo='PAIS')
    graficos = Grafico.objects.filter(abrangencia='PAIS', ativo=True).order_by('ordem')
    #print(graficos)
    variaveis_pais = Variavel.objects.filter(abrangencia='PAIS', ativa=True)
    #for a in variaveis_pais:
    #    print(a.unidade)
    #print(variaveis_pais)
    variaveis_graficos = VariaveisGrafico.objects.filter(grafico__in=list(graficos)).order_by('ordem')
    grafico_indice = 0
    for grafico in graficos:
        vars_graf = variaveis_graficos.filter(grafico=grafico.id).values('variavel')
        #print(vars_graf)
        vars_graf_var = variaveis_pais.filter(id__in=vars_graf).values('fonte')
        grafico_count_vars = vars_graf_var.count()
        fontes_graf = Fonte.objects.filter(id__in=vars_graf_var).distinct()
        grafico.fontes = fontes_graf
        if grafico_indice > 10:
            grafico_indice = 0
        grafico.indice = grafico_indice
        grafico.indice_cores = []
        for i in range(grafico_indice, (grafico_indice+grafico_count_vars)):
            if i > 10:
                grafico.indice_cores.append(i-10)
            else:
                grafico.indice_cores.append(i)
        grafico_indice += 1
    #print(variaveis_graficos)
    variaveis_pais_inteiro = VariavelPaisInteiro.objects.filter(pais=pais)
    data_atualizacao_vpi = variaveis_pais_inteiro.latest('atualizado_em')
    #print(variaveis_pais_inteiro)
    variaveis_pais_decimal = VariavelPaisDecimal.objects.filter(pais=pais)
    data_atualizacao_vpd = variaveis_pais_decimal.latest('atualizado_em')
    if data_atualizacao_vpi.atualizado_em > data_atualizacao_vpd.atualizado_em:
        ultima_atualizacao = _date(data_atualizacao_vpi.atualizado_em,"d/m/Y")
    else:
        ultima_atualizacao = _date(data_atualizacao_vpd.atualizado_em,"d/m/Y")
    #print(variaveis_pais_decimal)
    datas_variaveis_pais_inteiro = variaveis_pais_inteiro.values('data').distinct()
    #print(datas_variaveis_pais_inteiro)
    datas_variaveis_pais_decimal = variaveis_pais_decimal.values('data').distinct()
    #for i in variaveis_pais_decimal:
    #    print(i.valor)
    #print(datas_variaveis_pais_decimal)
    datas = datas_variaveis_pais_inteiro.union(datas_variaveis_pais_decimal).distinct().order_by('data')
    for data in datas:
        data['datafinal'] = _date(data['data'],"b/y")
    #print(datas)
    return render(
        request, 
        'dados/pais/pais_graficos.html', 
        {
            'pais' : pais,
            'ultima_atualizacao': ultima_atualizacao,
            'graficos': graficos,
            'datas': datas,
            'variaveis_pais': variaveis_pais,
            'variaveis_graficos': variaveis_graficos,
            'variaveis_pais_inteiro': variaveis_pais_inteiro,
            'variaveis_pais_decimal': variaveis_pais_decimal,
        }
    )

def tabelas_pais(request, pais):
    pais = get_object_or_404(Pais, nome_normalizado=pais)
    
    variaveis_pais_fontes = Variavel.objects.filter(abrangencia='PAIS', ativa=True).values('nome','ordem','fonte__nome','fonte__url').order_by('nome')
    vars_pais = Variavel.objects.filter(abrangencia='PAIS', ativa=True)
    
    val_pais_int = VariavelPaisInteiro.objects.filter(pais=pais).values('variavel__id','variavel__nome','data','atualizado_em','valor')
    val_pais_dec = VariavelPaisDecimal.objects.filter(pais=pais).values('variavel__id','variavel__nome','data','atualizado_em','valor')
    valores = val_pais_dec.union(val_pais_int)
    data_atualizacao = valores.latest('atualizado_em')
    ultima_atualizacao = _date(data_atualizacao['atualizado_em'],"d/m/Y")
    
    datas_vals_pais_int = val_pais_int.values('data').distinct().order_by('data')
    datas_vals_pais_dec = val_pais_dec.values('data').distinct().order_by('data')
    datas = datas_vals_pais_int.union(datas_vals_pais_dec).distinct().order_by('data')
    for data in datas:
        data['datafinal'] = _date(data['data'],"b/y")
    
    vars_pais_int = vars_pais.filter(unidade__in=['SEMU','INTE'])
    vars_pais_dec = vars_pais.filter(unidade__in=['DECI','REAL','DOLA','EURO','PORC'])
    val_pais_int_final = val_pais_int.values('variavel__id','data','valor','variavel__nome','variavel__unidade').order_by('data','variavel__nome')
    val_pais_dec_final = val_pais_dec.values('variavel__id','data','valor','variavel__nome','variavel__unidade').order_by('data','variavel__nome')
    
    for data in datas:
        val_pais_int_final_data_atual = val_pais_int_final.filter(data=data['data'])
        val_pais_dec_final_data_atual = val_pais_dec_final.filter(data=data['data'])
        union_val_data = val_pais_int_final_data_atual.union(val_pais_dec_final_data_atual).order_by('data','variavel__nome')
        data['valores'] = union_val_data
    
    #print(datas)
    return render(
        request, 
        'dados/pais/pais_tabelas.html', 
        {
            'pais' : pais,
            'datas' : datas,
            'vars_pais': vars_pais,
            'ultima_atualizacao' : ultima_atualizacao,
            'variaveis_pais_fontes' : variaveis_pais_fontes,
        }
    )
### End Pais ###
### Estado ###

def graficos_barra(grafico, datas_original, abrangencia, especificacao_abrangencia):
    datas = deepcopy(datas_original)
    vars_grafico = VariaveisGrafico.objects.filter(grafico=grafico)
    return grafico

def estados(request):
    pais = get_object_or_404(Pais, nome_normalizado='brasil')
    estados = Estado.objects.filter(pais=pais).values('nome', 'nome_normalizado')
    return render(
        request, 
        'dados/estado/estados.html', 
        {
            'estados' : estados,
        }
    )

def estado(request, estado):
    estado = get_object_or_404(Estado, nome_normalizado=estado)
    graficosrs = None
    if(estado == 'rio-grande-do-sul'):
        graficosrs = Grafico.objects.filter(abrangencia='ESRS')
    graficos = Grafico.objects.filter(abrangencia='ESTA')
    
    return render(
        request, 
        'dados/estado/estados.html', 
        {
            'graficosrs' : graficosrs
        }
    )

### Municipios ###

def municipio(request, municipio):
    estado = get_object_or_404(Estado, nome_normalizado='rio-grande-do-sul')
    municipios = Municipio.objects.filter(estado=estado).values('nome', 'nome_normalizado')
    return render(
        request, 
        'dados/municipio/municipios.html', 
        {
            'municipios' : municipios,
        }
    )

def municipios(request):
    """
    Municipios
    
    Exibe um mapa e uma lista com os municípios do estado do Rio Grande do Sul :model:`dados.Municipio`.

    **Context**
    
    ``municipios``
        Instâncias do modelo :model:`dados.Municipio` com filtro do estado do Rio Grande do Sul.
    
    **Template:**
    
    :template:`dados/municipio/municipios.html`
    """
    estado = get_object_or_404(Estado, nome_normalizado='rio-grande-do-sul')
    municipios = Municipio.objects.filter(estado=estado)
    return render(
        request, 
        'dados/municipio/municipios.html', 
        {
            'municipios' : municipios,
        }
    )

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