from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .forms import AbrangenciaForm, ContinenteForm, ImportarTabelaForm, RankingVarMuni, RankingVarEsta, RankingVarEstaMensal, RankingVarMuniMensal
from django.contrib.auth.decorators import login_required
from .processing.xlsx import ImportarDadosXSLX
from django.db.models import Sum, Count
from .models import Variavel, VariavelMunicipioInteiro, VariavelMunicipioDecimal, NoticiaExterna, Pais, Grafico, VariavelPais, VariaveisGrafico, VariavelPaisInteiro, VariavelPaisDecimal, VariavelEstadoInteiro, VariavelEstadoDecimal, Fonte, Estado, Municipio, Integrante, Documento, AutorDocumento, TextoOficial
from django.template.defaultfilters import date as _date
from django.db.models import Max
from copy import deepcopy
from django.db.models import Case, When
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from datetime import datetime

# Create your views here.
@login_required
def importar_dados(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar = ImportarDadosXSLX(request)  
            importar.importar_xlsx(request.FILES['tabela'])
            # if(resultado == 'Sucesso'):
            #     return HttpResponseRedirect('importar_dados?sucesso=Dados atualizados com sucesso!')
            # else:
            #     return HttpResponseRedirect('importar_dados?erro='+str(resultado))
    form = ImportarTabelaForm()
    return render(request, 'dados/importar_dados.html', {'form': form})

@login_required
def importar_municipios_rs(request):
    if request.method == 'POST':
        form = ImportarTabelaForm(request.POST, request.FILES)
        if form.is_valid():
            importar = ImportarDadosXSLX(request)  
            importar.importar_municipios_rs_xlsx(request.FILES['tabela'])
            # if(resultado == True):
            #     return HttpResponseRedirect('importar_municipios_rs?sucesso=Dados atualizados com sucesso!')
            # else:
            #     return HttpResponseRedirect('importar_municipios_rs?erro='+str(resultado))
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
    graficos = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'PAIS'
    
    graficos = graficos_ativos(abrangencia)
    
    datas = obter_datas_abrangencia(abrangencia, pais)
    if(datas != None):
        ultima_atualizacao = datas.ultima_atualizacao
    
    grafico_indice = 0 # Cores do Gráfico
    
    for grafico_atual in graficos:
        variaveis_grafico(grafico_atual)
        fontes_grafico(grafico_atual)
        # Cores do Gráfico
        grafico_count_vars = grafico_atual.vars_graf.count()
        if grafico_indice > 10:
            grafico_indice = 0
        grafico_atual.indice = grafico_indice
        grafico_atual.indice_cores = []
        for i in range(grafico_indice, (grafico_indice+grafico_count_vars)):
            if i > 10:
                grafico_atual.indice_cores.append(i-10)
            else:
                grafico_atual.indice_cores.append(i)
        grafico_indice += 1
        #end Cores do Grafico
        if(grafico_atual.tipo == 'LINH'):
            grafico_linhas_valores(grafico_atual, datas, abrangencia, pais)
    
    return render(
        request, 
        'dados/pais/pais_graficos.html', 
        {
            'pais' : pais,
            'graficos' : graficos,
            'ultima_atualizacao' : ultima_atualizacao,
        }
    )

def valores_tabela(datas, vars, abrangencia, especificacao_abrangencia):
    vars_int = vars.filter(unidade__in=['SEMU','INTE']).order_by('ordem').values('id')
    vars_dec = vars.filter(unidade__in=['DECI','REAL','DOLA','EURO','PORC']).order_by('ordem').values('id')
    
    if(abrangencia == 'PAIS'):
        vals_int = VariavelPaisInteiro.objects.filter(variavel__in=vars_int, pais=especificacao_abrangencia).order_by('variavel__ordem')
        vals_dec = VariavelPaisDecimal.objects.filter(variavel__in=vars_dec, pais=especificacao_abrangencia).order_by('variavel__ordem')
    elif(abrangencia == 'ESTA' or abrangencia == 'ESRS'):
        vals_int = VariavelEstadoInteiro.objects.filter(variavel__in=vars_int, estado=especificacao_abrangencia).order_by('variavel__ordem')
        vals_dec = VariavelEstadoDecimal.objects.filter(variavel__in=vars_dec, estado=especificacao_abrangencia).order_by('variavel__ordem')
    elif(abrangencia == 'MUNI'):
        vals_int = VariavelMunicipioInteiro.objects.filter(variavel__in=vars_int, municipio=especificacao_abrangencia).order_by('variavel__ordem')
        vals_dec = VariavelMunicipioDecimal.objects.filter(variavel__in=vars_dec, municipio=especificacao_abrangencia).order_by('variavel__ordem')
    
    vals_int = vals_int.values('variavel','variavel__unidade','valor','variavel__ordem','data')
    vals_dec = vals_dec.values('variavel','variavel__unidade','valor','variavel__ordem','data')
    
    valores = vals_int.union(vals_dec).order_by('variavel__ordem')
    
    for data in datas:
        data['datafinal'] = _date(data['data'],"b/y")
        vals_int_data = vals_int.filter(data=data['data'])
        vals_dec_data = vals_dec.filter(data=data['data'])
        valores = vals_int_data.union(vals_dec_data).order_by('variavel__ordem')
        if qs_possui_dados(valores):
            data['valores'] = valores
        else:
            data['valores'] = set()
    return datas

def variaveis_tabela(abrangencia):
    if(abrangencia == 'PAIS'):
        return Variavel.objects.filter(ativa=True, abrangencia='PAIS').values('nome','ordem','unidade','fonte__nome','fonte__url').order_by('ordem')
    elif(abrangencia == 'ESTA'):
        return Variavel.objects.filter(ativa=True, abrangencia='ESTA', variavel_exclusiva_do_estado_RS=False).values('nome','ordem','unidade','fonte__nome','fonte__url').order_by('ordem')
    elif(abrangencia == 'ESRS'):
        return Variavel.objects.filter(ativa=True, abrangencia='ESTA').values('nome','ordem','unidade','fonte__nome','fonte__url').order_by('ordem')
    elif(abrangencia == 'MUNI'):
        return Variavel.objects.filter(ativa=True, abrangencia='MUNI').values('nome','ordem','unidade','fonte__nome','fonte__url').order_by('ordem')
    else:
        return None

def tabelas_pais(request, pais):
    pais = get_object_or_404(Pais, nome_normalizado=pais)
    datas = None
    ultima_atualizacao = None
    vars = None
    abrangencia = 'PAIS'
    datas = obter_datas_abrangencia(abrangencia, pais)
    if(datas != None):
        ultima_atualizacao = datas.ultima_atualizacao
        vars = variaveis_tabela(abrangencia)
        datas = valores_tabela(datas, vars, abrangencia, pais)
    return render(
        request, 
        'dados/pais/pais_tabelas.html', 
        {
            'pais' : pais,
            'datas' : datas,
            'vars': vars,
            'ultima_atualizacao' : ultima_atualizacao,
        }
    )

### End Pais ###
### Estado ###

def tabelas_estado(request, estado):
    estado = get_object_or_404(Estado, nome_normalizado=estado)
    datas = None
    ultima_atualizacao = None
    abrangencia = 'ESTA'
    if(estado.nome_normalizado == 'rio-grande-do-sul'):
        abrangencia = 'ESRS'
    datas = obter_datas_abrangencia(abrangencia, estado)
    ultima_atualizacao = datas.ultima_atualizacao
    vars = variaveis_tabela(abrangencia)
    datas = valores_tabela(datas, vars, abrangencia, estado)
    return render(
        request, 
        'dados/estado/estado_tabelas.html', 
        {
            'estado' : estado,
            'datas' : datas,
            'vars': vars,
            'ultima_atualizacao' : ultima_atualizacao,
        }
    )

def graficos_ativos(abrangencia):
    """
    Graficos Ativos
    
    Retorna uma lista com os graficos ativos com a abrangencia selecionada :model:`dados.Grafico`.

    **Context**
    
    ``abrangencia``
        Filtro com 4 caracteres descrevendo a abrangencia :model:`dados.Grafico.ABRANGENCIA_GRAFICO`.
    """
    graficos = Grafico.objects.filter(ativo=True, abrangencia=abrangencia).order_by('ordem')
    return graficos

def variaveis_grafico(grafico):
    """
    Variaveis do Grafico
    
    Retorna uma lista com as variaveis do grafico informado :model:`dados.VariaveisGrafico`.

    **Context**
    
    ``grafico``
        Instancia de Grafico :model:`dados.Grafico`.
    """
    vars_graf = VariaveisGrafico.objects.filter(variavel__ativa=True, grafico=grafico)
    grafico.count_vars = 0
    vars_graf = vars_graf.values('grafico','variavel','ordem','variavel__nome','variavel__unidade','variavel__fonte').order_by('ordem')
    grafico.count_vars = vars_graf.count()
    grafico.vars_graf = vars_graf
    if(grafico.count_vars > 0):
        grafico.formato_eixo = grafico.vars_graf[0]['variavel__unidade']
    else:
        grafico.formato_eixo = None
    return grafico

def fontes_grafico(grafico):
    """
    Fontes do Grafico
    
    Adiciona uma lista com as fontes das variaveis do gráfico :model:`dados.Fonte` e retorna a instância do gráfico.

    **Context**
    
    ``grafico``
        Instancia de Grafico :model:`dados.Grafico`.
    ``vars_graf``
        Lista de Variáveis do Grafico :model:`dados.VariaveisGrafico`.
    """
    vars_graf_fontes = grafico.vars_graf.values('variavel__fonte')
    fontes = Fonte.objects.filter(id__in=vars_graf_fontes).distinct()
    grafico.fontes = fontes
    return

def qs_possui_dados(x):
    total_linhas = x.count()
    c = 0
    for a in x:
        if a['valor'] == None:
            c += 1
    if(c == total_linhas):
        return False
    return True

def grafico_linhas_valores(grafico, datas_original, abrangencia, especificacao_abrangencia):
    datas = deepcopy(datas_original) # Cópia da queryset com as datas, sem o campo data final, apenas com 'data':datetime
    
    vars_int = grafico.vars_graf.filter(variavel__unidade__in=['SEMU','INTE']).order_by('ordem').values('variavel')
    vars_dec = grafico.vars_graf.filter(variavel__unidade__in=['DECI','REAL','DOLA','EURO','PORC']).order_by('ordem').values('variavel')
    
    #ordenar qs conforme valores do array (atribute ordem from Model VariaveisGrafico) : https://stackoverflow.com/a/37648265/13593973
    vars_graf_array_int = [] #array com os ids das variaveis conforme ordem que devem ser exibidas no grafico
    for v in vars_int: # Criando array com os ids
        vars_graf_array_int.append(v['variavel'])
    vars_graf_array_dec = []
    for v in vars_dec:
        vars_graf_array_dec.append(v['variavel'])
    
    preserved_order_int = Case(*[When(variavel=variavel, then=pos) for pos, variavel in enumerate(vars_graf_array_int)])
    preserved_order_dec = Case(*[When(variavel=variavel, then=pos) for pos, variavel in enumerate(vars_graf_array_dec)])
    
    if(abrangencia == 'PAIS'):
        vals_int = VariavelPaisInteiro.objects.filter(variavel__in=vars_graf_array_int, pais=especificacao_abrangencia).order_by(preserved_order_int)
        vals_dec = VariavelPaisDecimal.objects.filter(variavel__in=vars_graf_array_dec, pais=especificacao_abrangencia).order_by(preserved_order_dec)
    elif(abrangencia == 'ESTA' or abrangencia == 'ESRS'):
        vals_int = VariavelEstadoInteiro.objects.filter(variavel__in=vars_graf_array_int, estado=especificacao_abrangencia).order_by(preserved_order_int)
        vals_dec = VariavelEstadoDecimal.objects.filter(variavel__in=vars_graf_array_dec, estado=especificacao_abrangencia).order_by(preserved_order_dec)
    elif(abrangencia == 'MUNI'):
        vals_int = VariavelMunicipioInteiro.objects.filter(variavel__in=vars_graf_array_int, municipio=especificacao_abrangencia).order_by(preserved_order_int)
        vals_dec = VariavelMunicipioDecimal.objects.filter(variavel__in=vars_graf_array_dec, municipio=especificacao_abrangencia).order_by(preserved_order_dec)
    
    vals_int = vals_int.values('variavel','variavel__unidade','valor')
    vals_dec = vals_dec.values('variavel','variavel__unidade','valor')
    
    valores = vals_int.union(vals_dec)
    #print(grafico.nome)
    for data in datas:
        data['datafinal'] = _date(data['data'],"b/y")
        vals_int_data = vals_int.filter(data=data['data'])
        vals_dec_data = vals_dec.filter(data=data['data'])
        valores = vals_int_data.union(vals_dec_data)
        #print(valores)
        if qs_possui_dados(valores):
            data['valores'] = valores
        else:
            data['valores'] = set()
    grafico.datas = datas
    return grafico

def estados(request):
    pais = get_object_or_404(Pais, nome_normalizado='brasil')
    estados = Estado.objects.filter(pais=pais).exclude(nome_normalizado='distrito-federal').values('nome', 'nome_normalizado')
    df = get_object_or_404(Estado, nome_normalizado='distrito-federal')
    return render(
        request, 
        'dados/estado/estados.html', 
        {
            'estados' : estados,
            'df' : df,
        }
    )

def obter_datas_abrangencia_sem_espec_abr(abrangencia):
    datas = None
    try:
        if(abrangencia == 'PAIS'):
            vars_pais_int = VariavelPaisInteiro.objects.all()
            datas_int = vars_pais_int.values('data').distinct().order_by('data')
            last_update_int = vars_pais_int.latest('atualizado_em')
            
            vars_pais_dec = VariavelPaisDecimal.objects.all()
            datas_dec = vars_pais_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_pais_dec.latest('atualizado_em')
        elif(abrangencia == 'ESTA' or abrangencia == 'ESRS'):
            vars_estado_int = VariavelEstadoInteiro.objects.all()
            datas_int = vars_estado_int.values('data').distinct().order_by('data')
            last_update_int = vars_estado_int.latest('atualizado_em')
            
            vars_estado_dec = VariavelEstadoDecimal.objects.all()
            datas_dec = vars_estado_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_estado_dec.latest('atualizado_em')
        elif(abrangencia == 'MUNI'):
            vars_municipio_int = VariavelMunicipioInteiro.objects.all()
            datas_int = vars_municipio_int.values('data').distinct().order_by('data')
            last_update_int = vars_municipio_int.latest('atualizado_em')
            
            vars_municipio_dec = VariavelMunicipioDecimal.objects.all()
            datas_dec = vars_municipio_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_municipio_dec.latest('atualizado_em')
            
        datas = datas_int.union(datas_dec)
            
        if(last_update_int.atualizado_em > last_update_dec.atualizado_em):
            data_atualizacao = last_update_int
        else:
            data_atualizacao = last_update_dec
            
        ultima_atualizacao = _date(data_atualizacao.atualizado_em,"d/m/Y")
        datas = datas.values('data').order_by('data')
        datas.ultima_atualizacao = ultima_atualizacao
    except:
        datas = None
    #deepcopy nao copia o datafinal, a criacao de datafinal ocorrera apos a copia em grafico_linhas_valores
    return datas

def obter_datas_abrangencia(abrangencia, especificacao_abrangencia):
    datas = None
    try:
        if(abrangencia == 'PAIS'):
            vars_pais_int = VariavelPaisInteiro.objects.filter(pais=especificacao_abrangencia)
            datas_int = vars_pais_int.values('data').distinct().order_by('data')
            last_update_int = vars_pais_int.latest('atualizado_em')
            
            vars_pais_dec = VariavelPaisDecimal.objects.filter(pais=especificacao_abrangencia)
            datas_dec = vars_pais_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_pais_dec.latest('atualizado_em')
        elif(abrangencia == 'ESTA' or abrangencia == 'ESRS'):
            vars_estado_int = VariavelEstadoInteiro.objects.filter(estado=especificacao_abrangencia)
            datas_int = vars_estado_int.values('data').distinct().order_by('data')
            last_update_int = vars_estado_int.latest('atualizado_em')
            
            vars_estado_dec = VariavelEstadoDecimal.objects.filter(estado=especificacao_abrangencia)
            datas_dec = vars_estado_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_estado_dec.latest('atualizado_em')
        elif(abrangencia == 'MUNI'):
            vars_municipio_int = VariavelMunicipioInteiro.objects.filter(municipio=especificacao_abrangencia)
            datas_int = vars_municipio_int.values('data').distinct().order_by('data')
            last_update_int = vars_municipio_int.latest('atualizado_em')
            
            vars_municipio_dec = VariavelMunicipioDecimal.objects.filter(municipio=especificacao_abrangencia)
            datas_dec = vars_municipio_dec.values('data').distinct().order_by('data')
            last_update_dec = vars_municipio_dec.latest('atualizado_em')
        datas = datas_int.union(datas_dec)
        
        if(last_update_int.atualizado_em > last_update_dec.atualizado_em):
            data_atualizacao = last_update_int
        else:
            data_atualizacao = last_update_dec
        
        ultima_atualizacao = _date(data_atualizacao.atualizado_em,"d/m/Y")
        datas = datas.values('data').order_by('data')
        datas.ultima_atualizacao = ultima_atualizacao
    except:
        datas = None
    #deepcopy nao copia o datafinal, a criacao de datafinal ocorrera apos a copia em grafico_linhas_valores
    return datas

def estado(request, estado):
    estado = get_object_or_404(Estado, nome_normalizado=estado)
    graficos = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'ESTA'
    
    if(estado.nome_normalizado == 'rio-grande-do-sul'):
        abrangencia = 'ESRS'
    graficos = graficos_ativos(abrangencia)
    
    datas = obter_datas_abrangencia(abrangencia, estado)
    if(datas != None):
        ultima_atualizacao = datas.ultima_atualizacao
        
        grafico_indice = 0 # Cores do Gráfico
        
        for grafico_atual in graficos:
            variaveis_grafico(grafico_atual)
            fontes_grafico(grafico_atual)
            # Cores do Gráfico
            grafico_count_vars = grafico_atual.vars_graf.count()
            if grafico_indice > 10:
                grafico_indice = 0
            grafico_atual.indice = grafico_indice
            grafico_atual.indice_cores = []
            for i in range(grafico_indice, (grafico_indice+grafico_count_vars)):
                if i > 10:
                    grafico_atual.indice_cores.append(i-10)
                else:
                    grafico_atual.indice_cores.append(i)
            grafico_indice += 1
            #end Cores do Grafico
            if(grafico_atual.tipo == 'LINH'):
                grafico_linhas_valores(grafico_atual, datas, abrangencia, estado)
    else:
        graficos = None
        ultima_atualizacao = '-'
        messages.info(request, str('Aviso: Não foram encontrados dados para o estado: '+estado.nome+'.'))
    return render(
        request, 
        'dados/estado/estado_graficos.html', 
        {
            'estado' : estado,
            'graficos' : graficos,
            'ultima_atualizacao' : ultima_atualizacao,
        }
    )

### Municipios ###

def municipio(request, municipio):
    estado = get_object_or_404(Estado, nome_normalizado='rio-grande-do-sul')
    municipio = get_object_or_404(Municipio, estado=estado, nome_normalizado=municipio)
    graficos = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'MUNI'
    
    graficos = graficos_ativos(abrangencia)
    
    datas = obter_datas_abrangencia(abrangencia, municipio)
    if(datas != None):
        ultima_atualizacao = datas.ultima_atualizacao
        
        grafico_indice = 0 # Cores do Gráfico
        
        for grafico_atual in graficos:
            variaveis_grafico(grafico_atual)
            fontes_grafico(grafico_atual)
            # Cores do Gráfico
            grafico_count_vars = grafico_atual.vars_graf.count()
            if grafico_indice > 10:
                grafico_indice = 0
            grafico_atual.indice = grafico_indice
            grafico_atual.indice_cores = []
            for i in range(grafico_indice, (grafico_indice+grafico_count_vars)):
                if i > 10:
                    grafico_atual.indice_cores.append(i-10)
                else:
                    grafico_atual.indice_cores.append(i)
            grafico_indice += 1
            #end Cores do Grafico
            if(grafico_atual.tipo == 'LINH'):
                grafico_linhas_valores(grafico_atual, datas, abrangencia, municipio)
    else:
        graficos = None
        ultima_atualizacao = '-'
        messages.info(request, str('Aviso: Não foram encontrados dados para o municipio: '+municipio.nome+'.'))
    return render(
        request, 
        'dados/municipio/municipio_graficos.html', 
        {
            'municipio' : municipio,
            'graficos' : graficos,
            'ultima_atualizacao' : ultima_atualizacao,
        }
    )

def tabelas_municipio(request, municipio):
    estado = get_object_or_404(Estado, nome_normalizado='rio-grande-do-sul')
    municipio = get_object_or_404(Municipio, nome_normalizado=municipio)
    datas = None
    ultima_atualizacao = None
    abrangencia = 'MUNI'
    datas = obter_datas_abrangencia(abrangencia, municipio)
    ultima_atualizacao = datas.ultima_atualizacao
    vars = variaveis_tabela(abrangencia)
    datas = valores_tabela(datas, vars, abrangencia, municipio)
    return render(
        request, 
        'dados/municipio/municipio_tabelas.html', 
        {
            'municipio' : municipio,
            'datas' : datas,
            'vars': vars,
            'ultima_atualizacao' : ultima_atualizacao,
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

def variavel_is_int(unidade):
        if(unidade == 'INTE' or unidade == 'SEMU'):
            return True
        return False
    
def variavel_is_dec(unidade):
    if(unidade == 'DECI' or unidade == 'REAL' or unidade == 'DOLA' or unidade == 'EURO' or unidade == 'PORC'):
        return True
    return False

def rank_municipios(request):
    if request.method == 'GET':
        form = RankingVarMuni(request.GET)
        if form.is_valid():
            return rank_var_municipio(request)
        else:
            form = RankingVarMuni()
            return render(request, 'dados/municipio/ranking.html', {'form': form})

def rank_municipios_mensal(request):
    if request.method == 'GET':
        form = RankingVarMuniMensal(request.GET)
        if form.is_valid():
            return rank_var_municipio_mensal(request)
        else:
            form = RankingVarMuniMensal()
            return render(request, 'dados/municipio/ranking_mensal.html', {'form': form})

def rank_var_municipio(request):
    variavel = request.GET['variavel']
    periodo = request.GET['periodo']
    variavel = get_object_or_404(Variavel, id=variavel)
    dados = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'MUNI'
    datas = obter_datas_abrangencia_sem_espec_abr(abrangencia)
    ultima_atualizacao = datas.ultima_atualizacao
    if(variavel_is_int(variavel.unidade)):
        if(periodo == 'Todos'):
            dados = VariavelMunicipioInteiro.objects.filter(variavel=variavel).values('municipio','municipio__nome','municipio__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('variavel__nome','-soma')
        else:
            dados = VariavelMunicipioInteiro.objects.filter(variavel=variavel, data__year=periodo).values('municipio','municipio__nome','municipio__nome_normalizado', 'variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('variavel__nome','-soma')
    elif(variavel_is_dec(variavel.unidade)):
        if(periodo == 'Todos'):
            dados = VariavelMunicipioDecimal.objects.filter(variavel=variavel).values('municipio','municipio__nome','municipio__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
        else:
            dados = VariavelMunicipioDecimal.objects.filter(variavel=variavel, data__year=periodo).values('municipio','municipio__nome','municipio__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    return render(
        request, 
        'dados/municipio/ranking_var_periodo.html', 
        {
            'dados' : dados,
            'variavel' : variavel,
            'periodo' : periodo,
            'ultima_atualizacao': ultima_atualizacao,
        }
    )

def rank_var_municipio_mensal(request):
    variavel = request.GET['variavel']
    periodo = request.GET['periodo']
    periodosplit = periodo.split('-')
    year = int(periodosplit[0])
    month = int(periodosplit[1])
    day = int(periodosplit[2])
    periodo = datetime(year=year, month=month, day=day)
    periodoview = periodosplit[1]+'/'+periodosplit[0]
    variavel = get_object_or_404(Variavel, id=variavel)
    dados = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'MUNI'
    datas = obter_datas_abrangencia_sem_espec_abr(abrangencia)
    ultima_atualizacao = datas.ultima_atualizacao
    if(variavel_is_int(variavel.unidade)):
        dados = VariavelMunicipioInteiro.objects.filter(variavel=variavel, data=periodo).exclude(valor__isnull=True).values('municipio','municipio__nome','municipio__nome_normalizado', 'variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    elif(variavel_is_dec(variavel.unidade)):
        dados = VariavelMunicipioDecimal.objects.filter(variavel=variavel, data=periodo).exclude(valor__isnull=True).values('municipio','municipio__nome','municipio__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    if dados.count() == 0:
        dados = None
        messages.info(request, str('Aviso: Não foram encontrados dados para a variável: '+variavel.nome+' no período selecionado: '+periodoview+'.'))
    return render(
        request, 
        'dados/municipio/ranking_var_periodo.html', 
        {
            'dados' : dados,
            'variavel' : variavel,
            'periodo' : periodoview,
            'mensal': True,
            'ultima_atualizacao': ultima_atualizacao,
        }
    )

def rank_estados(request):
    if request.method == 'GET':
        form = RankingVarEsta(request.GET)
        if form.is_valid():
            return rank_var_estado(request)
        else:
            form = RankingVarEsta()
            return render(request, 'dados/estado/ranking.html', {'form': form})

def rank_estados_mensal(request):
    if request.method == 'GET':
        form = RankingVarEstaMensal(request.GET)
        if form.is_valid():
            return rank_var_estado_mensal(request)
        else:
            form = RankingVarEstaMensal()
            return render(request, 'dados/estado/ranking_mensal.html', {'form': form})

def rank_var_estado_mensal(request):
    variavel = request.GET.get('variavel')
    periodo = request.GET.get('periodo')
    periodosplit = periodo.split('-')
    year = int(periodosplit[0])
    month = int(periodosplit[1])
    day = int(periodosplit[2])
    periodo = datetime(year=year, month=month, day=day)
    periodoview = periodosplit[1]+'/'+periodosplit[0]
    variavel = get_object_or_404(Variavel, id=variavel)
    dados = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'ESTA'
    datas = obter_datas_abrangencia_sem_espec_abr(abrangencia)
    ultima_atualizacao = datas.ultima_atualizacao
    if(variavel_is_int(variavel.unidade)):
        dados = VariavelEstadoInteiro.objects.filter(variavel=variavel, data=periodo).exclude(valor__isnull=True).values('estado','estado__nome','estado__nome_normalizado', 'variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    elif(variavel_is_dec(variavel.unidade)):
        dados = VariavelEstadoDecimal.objects.filter(variavel=variavel, data=periodo).exclude(valor__isnull=True).values('estado','estado__nome','estado__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    if dados.count() == 0:
        dados = None
        messages.info(request, str('Aviso: Não foram encontrados dados para a variável: '+variavel.nome+' no período selecionado: '+periodoview+'.'))
    return render(
        request, 
        'dados/estado/ranking_var_periodo.html', 
        {
            'dados' : dados,
            'variavel' : variavel,
            'periodo' : periodoview,
            'mensal': True,
            'ultima_atualizacao': ultima_atualizacao,
        }
    )

def rank_var_estado(request):
    variavel = request.GET.get('variavel')
    periodo = request.GET.get('periodo')
    variavel = get_object_or_404(Variavel, id=variavel)
    dados = None
    datas = None
    ultima_atualizacao = None
    abrangencia = 'ESTA'
    datas = obter_datas_abrangencia_sem_espec_abr(abrangencia)
    ultima_atualizacao = datas.ultima_atualizacao
    if(variavel_is_int(variavel.unidade)):
        if(periodo == 'Todos'):
            dados = VariavelEstadoInteiro.objects.filter(variavel=variavel).values('estado','estado__nome','estado__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
        else:
            dados = VariavelEstadoInteiro.objects.filter(variavel=variavel, data__year=periodo).values('estado','estado__nome','estado__nome_normalizado', 'variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    elif(variavel_is_dec(variavel.unidade)):
        if(periodo == 'Todos'):
            dados = VariavelEstadoDecimal.objects.filter(variavel=variavel).values('estado','estado__nome','estado__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
        else:
            dados = VariavelEstadoDecimal.objects.filter(variavel=variavel, data__year=periodo).values('estado','estado__nome','estado__nome_normalizado','variavel__nome','variavel__unidade').annotate(soma=Sum('valor')).order_by('-soma')
    return render(
        request, 
        'dados/estado/ranking_var_periodo.html', 
        {
            'dados' : dados,
            'variavel' : variavel,
            'periodo' : periodo,
            'ultima_atualizacao': ultima_atualizacao,
        }
    )

### End Dados ###

def equipe(request):
    coordenacao = Integrante.objects.filter(equipe='COOR').order_by('ordem')
    executiva = Integrante.objects.filter(equipe='EXEC').order_by('ordem')
    operacional = Integrante.objects.filter(equipe='OPER').order_by('ordem')
    apoiadora = Integrante.objects.filter(equipe='APOI').order_by('ordem')
    colaborativa = Integrante.objects.filter(equipe='COLA').order_by('ordem')
    financiadora = Integrante.objects.filter(equipe='FINA').order_by('ordem')
    return render(
        request, 
        'dados/equipe.html', 
        {
            'coordenacao' : coordenacao,
            'executiva' : executiva,
            'operacional' : operacional,
            'apoiadora' : apoiadora,
            'colaborativa' : colaborativa,
            'financiadora' : financiadora,
        }
    )

def analises_de_conjuntura(request):
    return documentos(request, 'CONJ', 'dados/analise_de_conjuntura.html')

def textos_para_discussao(request):
    return documentos(request, 'DISC', 'dados/textos_para_discussao.html')

def documentos(request, tipo, template):
    documents = None
    documents_list = Documento.objects.filter(tipo=tipo).order_by('-numero')
    for d in documents_list:
        d.list_autores = AutorDocumento.objects.filter(documento=d).values('documento','autor','autor__nome','ordem').order_by('ordem')
    paginator = Paginator(documents_list, 10)
    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    return render(
        request, 
        template, 
        {
            'page' : page,
            'documents' : documents,
        }
    )

def textos_oficiais(request):
    return render(
        request, 
        'dados/textos_oficiais.html', 
    )

def textos_oficiais_lista_abr(request, abrangencia, nome_normalizado):
    documents = None
    texts_list = None
    abrangencia_desc = ""
    espec_abr = set()
    if(abrangencia=='PAIS'):
        abrangencia_desc = 'Pais'
        pais = get_object_or_404(Pais, nome_normalizado=nome_normalizado)
        texts_list = TextoOficial.objects.filter(pais=pais).order_by('-data')
        espec_abr = pais
    elif(abrangencia=='ESTA'):
        abrangencia_desc = 'Estado'
        estado = get_object_or_404(Estado, nome_normalizado=nome_normalizado)
        texts_list = textos_list = TextoOficial.objects.filter(estado=estado).order_by('-data')
        espec_abr = estado
    paginator = Paginator(texts_list, 10)
    page = request.GET.get('page')
    if(texts_list.count() == 0):
        messages.info(request, str('Aviso: Não foram encontrados textos oficiais para o '+abrangencia_desc+': '+espec_abr.nome+'.'))
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    return render(
        request, 
        'dados/textos_oficiais_list.html', 
        {
            'page' : page,
            'documents' : documents,
            'abrangencia' : abrangencia_desc,
            'espec_abr' : espec_abr,
        }
    )

def textos_oficiais_abr_pais(request, pais):
    return textos_oficiais_lista_abr(request, 'PAIS', pais)

def textos_oficiais_abr_estado(request, estado):
    return textos_oficiais_lista_abr(request, 'ESTA', estado)

@login_required
def contagem_dados(request):
    paisInt = VariavelPaisInteiro.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    paisDec = VariavelPaisDecimal.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    #print('paisInt:',paisInt,', paisDec:', paisDec)
    cont_dados_paises = int(paisInt) + int(paisDec)
    
    estadoInt = VariavelEstadoInteiro.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    estadoDec = VariavelEstadoDecimal.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    #print('estadoint:',estadoInt,', estadodec:', estadoDec)
    cont_dados_estados = int(estadoInt) + int(estadoDec)
    
    municipioInt = VariavelMunicipioInteiro.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    municipioDec = VariavelMunicipioDecimal.objects.filter(variavel__ativa=True).exclude(valor__isnull=True).count()
    #print('municipioInt:',municipioInt,', municipioDec:', municipioDec)
    cont_dados_municipios = int(municipioInt) + int(municipioDec)
    
    cont_dados_total = cont_dados_paises + cont_dados_estados + cont_dados_municipios
    return render(
        request,
        'dados/dashboard.html',  
        {
            'cont_dados_estados' : cont_dados_estados,
            'cont_dados_paises' : cont_dados_paises,
            'cont_dados_municipios' : cont_dados_municipios,
            'cont_dados_total' : cont_dados_total,
        }
    )