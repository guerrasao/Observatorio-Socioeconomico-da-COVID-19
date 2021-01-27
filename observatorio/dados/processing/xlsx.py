import pandas as pd
from django.db import models
from django.utils.text import slugify
from ..models import Pais, Estado, Municipio, Variavel, VariavelPaisInteiro, VariavelPaisDecimal, VariavelEstadoInteiro, VariavelEstadoDecimal, VariavelMunicipioInteiro, VariavelMunicipioDecimal

def importar_xlsx(arquivo):
    conteudo_arquivo = arquivo.read()
    controle = pd.read_excel(conteudo_arquivo, sheet_name='Controle')
    print(controle)
    abrangencia = controle.at[0,'abrangencia']
    if(abrangencia != 'MUNI'):
        dados = pd.read_excel(conteudo_arquivo, sheet_name='Dados')
        #replace NaN with None
        dados = dados.astype(object).where(pd.notnull(dados),None)
        print(dados)
    
    if(abrangencia == 'PAIS'):
        pais = Pais.objects.get(nome_normalizado=controle.at[0, 'nome_normalizado'])
        variaveis_pais = Variavel.objects.all().filter(abrangencia='PAIS', ativa=True)
        variaveis_pais_int = VariavelPaisInteiro.objects.all()
        variaveis_pais_dec = VariavelPaisDecimal.objects.all()
        #print(variaveis_pais)
        variaveis_tab = dados.columns
        linhas_tab = dados.index
        for linha_atual in linhas_tab:
            for var_atual in variaveis_tab:
                if((var_atual != 'Data') and (var_atual != 'Tempo/Variável')):
                    var_atual_obj = variaveis_pais.filter(nome=var_atual).values()
                    #print(var_atual_obj[0]['unidade'])
                    if(var_atual_obj[0]['unidade'] == 'SEMU' or var_atual_obj[0]['unidade'] == 'INTE'):
                        linha_existe = VariavelPaisInteiro.objects.filter(pais=pais, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                        print(linha_existe)
                        cont_linha_existe = linha_existe.count()
                        print(cont_linha_existe)
                        #linha não existe, adicionar
                        if cont_linha_existe == 0: 
                            l = VariavelPaisInteiro(
                                    variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                    pais = pais,
                                    data = dados.at[linha_atual, 'Data'],
                                    valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                )
                            l.save()
                        #linha existe, atualizar
                        elif cont_linha_existe == 1:
                            print(linha_existe)
                            print(linha_existe.values())
                            l = VariavelPaisInteiro.objects.get(id=linha_existe.values()[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        else:
                            #a primeira linha a ser mantida, excluindo a inconsistencia
                            vet_linhas_existentes = linha_existe[1:]
                            for atual in vet_linhas_existentes:
                                l = VariavelPaisInteiro.objects.get(id=atual[0]['id'])
                                l.delete()
                            #atualiza o valor da linha
                            l = VariavelPaisInteiro.objects.get(id=linha_existe[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                    elif(
                        var_atual_obj[0]['unidade'] == 'DECI' or
                        var_atual_obj[0]['unidade'] == 'REAL' or 
                        var_atual_obj[0]['unidade'] == 'DOLA' or 
                        var_atual_obj[0]['unidade'] == 'EURO' or 
                        var_atual_obj[0]['unidade'] == 'PORC'
                        ):
                        linha_existe = VariavelPaisDecimal.objects.filter(pais=pais, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                        print(linha_existe)
                        cont_linha_existe = linha_existe.count()
                        print(cont_linha_existe)
                        #linha não existe, adicionar
                        if cont_linha_existe == 0: 
                            l = VariavelPaisDecimal(
                                    variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                    pais = pais,
                                    data = dados.at[linha_atual, 'Data'],
                                    valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                )
                            l.save()
                        #linha existe, atualizar
                        elif cont_linha_existe == 1:
                            print(linha_existe)
                            print(linha_existe.values())
                            l = VariavelPaisDecimal.objects.get(id=linha_existe.values()[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        else:
                            #a primeira linha a ser mantida, excluindo a inconsistencia
                            vet_linhas_existentes = linha_existe[1:]
                            for atual in vet_linhas_existentes:
                                l = VariavelPaisDecimal.objects.get(id=atual[0]['id'])
                                l.delete()
                            #atualiza o valor da linha
                            l = VariavelPaisDecimal.objects.get(id=linha_existe[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                    else:
                        print('Tipo de Variavel não identificado:', var_atual_obj[0]['unidade'])
        print(variaveis_tab)
    elif(abrangencia == 'ESTA'):
        estado = Estado.objects.get(nome_normalizado=controle.at[0, 'nome_normalizado'])
        if(controle.at[0, 'nome_normalizado'] == 'rio-grande-do-sul'):
            variaveis_estado = Variavel.objects.all().filter(abrangencia='ESTA', ativa=True)
        else:
            variaveis_estado = Variavel.objects.all().filter(abrangencia='ESTA', ativa=True, variavel_exclusiva_do_estado_RS=False)
        variaveis_estado = Variavel.objects.all().filter(abrangencia='ESTA', ativa=True)
        variaveis_estado_int = VariavelEstadoInteiro.objects.all()
        variaveis_estado_dec = VariavelEstadoDecimal.objects.all()
        print(variaveis_estado)
        variaveis_tab = dados.columns
        linhas_tab = dados.index
        for linha_atual in linhas_tab:
            for var_atual in variaveis_tab:
                if((var_atual != 'Data') and (var_atual != 'Tempo/Variável')):
                    var_atual_obj = variaveis_estado.filter(nome=var_atual).values()
                    #print(var_atual_obj[0]['unidade'])
                    if(var_atual_obj[0]['unidade'] == 'SEMU' or var_atual_obj[0]['unidade'] == 'INTE'):
                        linha_existe = VariavelEstadoInteiro.objects.filter(estado=estado, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                        print(linha_existe)
                        cont_linha_existe = linha_existe.count()
                        print(cont_linha_existe)
                        #linha não existe, adicionar
                        if cont_linha_existe == 0: 
                            l = VariavelEstadoInteiro(
                                    variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                    estado = estado,
                                    data = dados.at[linha_atual, 'Data'],
                                    valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                )
                            l.save()
                        #linha existe, atualizar
                        elif cont_linha_existe == 1:
                            print(linha_existe)
                            print(linha_existe.values())
                            l = VariavelEstadoInteiro.objects.get(id=linha_existe.values()[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        else:
                            #a primeira linha a ser mantida, excluindo a inconsistencia
                            vet_linhas_existentes = linha_existe[1:]
                            for atual in vet_linhas_existentes:
                                l = VariavelEstadoInteiro.objects.get(id=atual[0]['id'])
                                l.delete()
                            #atualiza o valor da linha
                            l = VariavelEstadoInteiro.objects.get(id=linha_existe[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                    elif(
                        var_atual_obj[0]['unidade'] == 'DECI' or
                        var_atual_obj[0]['unidade'] == 'REAL' or 
                        var_atual_obj[0]['unidade'] == 'DOLA' or 
                        var_atual_obj[0]['unidade'] == 'EURO' or 
                        var_atual_obj[0]['unidade'] == 'PORC'
                        ):
                        linha_existe = VariavelEstadoDecimal.objects.filter(estado=estado, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                        print(linha_existe)
                        cont_linha_existe = linha_existe.count()
                        print(cont_linha_existe)
                        #linha não existe, adicionar
                        if cont_linha_existe == 0: 
                            l = VariavelEstadoDecimal(
                                    variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                    estado = estado,
                                    data = dados.at[linha_atual, 'Data'],
                                    valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                )
                            l.save()
                        #linha existe, atualizar
                        elif cont_linha_existe == 1:
                            print(linha_existe)
                            print(linha_existe.values())
                            l = VariavelEstadoDecimal.objects.get(id=linha_existe.values()[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        else:
                            #a primeira linha a ser mantida, excluindo a inconsistencia
                            vet_linhas_existentes = linha_existe[1:]
                            for atual in vet_linhas_existentes:
                                l = VariavelEstadoDecimal.objects.get(id=atual[0]['id'])
                                l.delete()
                            #atualiza o valor da linha
                            l = VariavelEstadoDecimal.objects.get(id=linha_existe[0]['id'])
                            l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                            l.save()
                        #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                    else:
                        print('Tipo de Variavel não identificado:', var_atual_obj[0]['unidade'])
        print()
    elif(abrangencia == 'MUNI'):
        municipios = pd.read_excel(conteudo_arquivo, sheet_name='Municipios')
        municipios = municipios.astype(object).where(pd.notnull(municipios),None)
        print(municipios)
        #replace NaN with None
        #dados = dados.astype(object).where(pd.notnull(dados),None)
        #print(dados)
        
        estado = Estado.objects.get(nome_normalizado=controle.at[0, 'nome_normalizado'])
        variaveis_municipio = Variavel.objects.all().filter(abrangencia='MUNI', ativa=True)
        variaveis_municipio_int = VariavelMunicipioInteiro.objects.all()
        variaveis_municipio_dec = VariavelMunicipioDecimal.objects.all()
        print(variaveis_municipio)
        
        municipios_index = municipios.index
        for municipio_atual in municipios_index:
            dados = pd.read_excel(conteudo_arquivo, sheet_name=municipios.at[municipio_atual, 'Nome_Normalizado'])
            dados = dados.astype(object).where(pd.notnull(dados),None)
            print(dados)
            
            municipio = Municipio.objects.get(codigo_ibge=municipios.at[municipio_atual, 'Codigo_IBGE'])

            variaveis_tab = dados.columns
            linhas_tab = dados.index
            for linha_atual in linhas_tab:
                for var_atual in variaveis_tab:
                    if((var_atual != 'Data') and (var_atual != 'Tempo/Variável')):
                        var_atual_obj = variaveis_municipio.filter(nome=var_atual).values()
                        #print(var_atual_obj[0]['unidade'])
                        if(var_atual_obj[0]['unidade'] == 'SEMU' or var_atual_obj[0]['unidade'] == 'INTE'):
                            linha_existe = VariavelMunicipioInteiro.objects.filter(municipio=municipio, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                            print(linha_existe)
                            cont_linha_existe = linha_existe.count()
                            print(cont_linha_existe)
                            #linha não existe, adicionar
                            if cont_linha_existe == 0: 
                                l = VariavelMunicipioInteiro(
                                        variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                        municipio = municipio,
                                        data = dados.at[linha_atual, 'Data'],
                                        valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                    )
                                l.save()
                            #linha existe, atualizar
                            elif cont_linha_existe == 1:
                                print(linha_existe)
                                print(linha_existe.values())
                                l = VariavelMunicipioInteiro.objects.get(id=linha_existe.values()[0]['id'])
                                l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                l.save()
                            else:
                                #a primeira linha a ser mantida, excluindo a inconsistencia
                                vet_linhas_existentes = linha_existe[1:]
                                for atual in vet_linhas_existentes:
                                    l = VariavelMunicipioInteiro.objects.get(id=atual[0]['id'])
                                    l.delete()
                                #atualiza o valor da linha
                                l = VariavelMunicipioInteiro.objects.get(id=linha_existe[0]['id'])
                                l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                l.save()
                            #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                        elif(
                            var_atual_obj[0]['unidade'] == 'DECI' or
                            var_atual_obj[0]['unidade'] == 'REAL' or 
                            var_atual_obj[0]['unidade'] == 'DOLA' or 
                            var_atual_obj[0]['unidade'] == 'EURO' or 
                            var_atual_obj[0]['unidade'] == 'PORC'
                            ):
                            linha_existe = VariavelMunicipioDecimal.objects.filter(municipio=municipio, data=dados.at[linha_atual, 'Data'], variavel = var_atual_obj[0]['id']).order_by('-atualizado_em')
                            print(linha_existe)
                            cont_linha_existe = linha_existe.count()
                            print(cont_linha_existe)
                            #linha não existe, adicionar
                            if cont_linha_existe == 0: 
                                l = VariavelMunicipioDecimal(
                                        variavel = Variavel.objects.get(id=var_atual_obj[0]['id']),
                                        municipio = municipio,
                                        data = dados.at[linha_atual, 'Data'],
                                        valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                    )
                                l.save()
                            #linha existe, atualizar
                            elif cont_linha_existe == 1:
                                print(linha_existe)
                                print(linha_existe.values())
                                l = VariavelMunicipioDecimal.objects.get(id=linha_existe.values()[0]['id'])
                                l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                l.save()
                            else:
                                #a primeira linha a ser mantida, excluindo a inconsistencia
                                vet_linhas_existentes = linha_existe[1:]
                                for atual in vet_linhas_existentes:
                                    l = VariavelMunicipioDecimal.objects.get(id=atual[0]['id'])
                                    l.delete()
                                #atualiza o valor da linha
                                l = VariavelMunicipioDecimal.objects.get(id=linha_existe[0]['id'])
                                l.valor = dados.at[linha_atual, var_atual_obj[0]['nome']]
                                l.save()
                            #erro mais de uma linha encontrada com a combinação de chaves, remover e deixar a última apenas
                        else:
                            print('Tipo de Variavel não identificado:', var_atual_obj[0]['unidade'])
        print()
    elif(abrangencia == 'CONT'):
        print()
    else:
        return "Erro na leitura da abrangencia"
    return True

def importar_municipios_rs_xlsx(arquivo):
    conteudo_arquivo = arquivo.read()
    dados = pd.read_excel(conteudo_arquivo, sheet_name='Municipios')
    print(dados)
    linhas_tab = dados.index
    estado = Estado.objects.get(nome_normalizado='rio-grande-do-sul')
    u = 0
    a = 0
    for linha_atual in linhas_tab:
        municipio_existe = Municipio.objects.filter(estado=estado, nome_normalizado=slugify(dados.at[linha_atual, 'nome']))
        # inserir sem coluna de numero de habitantes
        if(municipio_existe.count() == 0):
            l = Municipio(
                estado = estado,
                codigo_ibge = dados.at[linha_atual, 'id'],
                nome = dados.at[linha_atual, 'nome'],
                #numero_habitantes = dados.at[linha_atual, 'numero_habitantes'],
            )
            l.save()
            a += 1
        #atualizar municipio com o numero de habitantes
        else:
            municipio_atual = Municipio.objects.get(nome_normalizado=slugify(dados.at[linha_atual, 'nome']))
            #print(municipio_atual)
            municipio_atual.numero_habitantes = dados.at[linha_atual, 'numero_habitantes']
            municipio_atual.total_de_repasse_programa_apoio_financeiro = dados.at[linha_atual, 'total_de_repasse_programa_apoio_financeiro']
            municipio_atual.save()
            u += 1
    print('Linhas atualizadas:', u, ', Municipios Inseridos:', a)