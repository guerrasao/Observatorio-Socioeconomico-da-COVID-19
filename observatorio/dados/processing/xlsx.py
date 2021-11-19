import pandas as pd
from django.db import models, transaction, Error
from django.utils.text import slugify
from ..models import Pais, Estado, Municipio, Variavel, VariavelPaisInteiro, VariavelPaisDecimal, VariavelEstadoInteiro, VariavelEstadoDecimal, VariavelMunicipioInteiro, VariavelMunicipioDecimal
from django.contrib import messages
from django.template.defaultfilters import date as _date

class ImportarDadosXSLX:
    def __init__(self, request):
        self.request = request
        self.c_geral = 0
        self.c_cadastro = 0
        self.c_atualizacao = 0
    
    def abrangencia_str(self, abrangencia):
        if(abrangencia == 'PAIS'):
            return 'Paises'
        elif(abrangencia == 'ESTA'):
            return 'Estados'
        elif(abrangencia == 'MUNI'):
            return 'Municipios'
        return '(Erro: Abrangencia encontrada no arquivo não é válida)'
    
    def abrangencia_str_atributo_model(self, abrangencia):
        if(abrangencia == 'PAIS'):
            return 'pais'
        elif(abrangencia == 'ESTA'):
            return 'estado'
        elif(abrangencia == 'MUNI'):
            return 'municipio'
        return '(Erro: Abrangencia encontrada no arquivo não é válida)'
    
    def valor_unico_lc(self, nome_tabela, dados, linha, coluna):
        try:
            return dados.at[linha, coluna]
        except:
            messages.error(self.request, str('Erro na Leitura da tabela '+ nome_tabela +', linha '+str(linha+1)+' e coluna '+str(coluna)+'.'))
            return False
    
    def ler_arquivo(self, arquivo):
        try:
            return arquivo.read()
        except:
            messages.error(self.request, 'Erro: Não foi possível realizar leitura do arquivo enviado, tente novamente!')
            return False
    
    def ler_tabela(self, conteudo_arquivo, tabela):
        try:
            return pd.read_excel(conteudo_arquivo, sheet_name=tabela)
        except:
            messages.error(self.request, str('Erro na Leitura da tabela: '+tabela+'.'))
            return False
    
    def obter_abrangencia_arq(self, controle):
        return self.valor_unico_lc('controle', controle, 0, 'abrangencia')
    
    def replaceNaNWithNone(self, dados):
        try:
            return dados.astype(object).where(pd.notnull(dados),None)
        except:
            messages.error(self.request, 'Erro no tratamento dados sem valor.')
            return False
    
    def lista_especificacao_abrangencia(self, conteudo_arquivo, abrangencia): #lista de paises, estados ou municipios
        try:
            return self.ler_tabela(conteudo_arquivo, self.abrangencia_str(abrangencia))
        except:
            messages.error(self.request, str('Erro: Não foi possível ler a tabela com a lista de '+self.abrangencia_str(abrangencia)+' do arquivo.'))
            return False
    
    def obter_vars_abr(self, abrangencia):
        try:
            if(abrangencia == 'PAIS'):
                return Variavel.objects.filter(abrangencia='PAIS')
            elif(abrangencia == 'ESTA'):
                return Variavel.objects.filter(abrangencia='ESTA')
            elif(abrangencia == 'MUNI'):
                return Variavel.objects.filter(abrangencia='MUNI')
            else:
                messages.error(self.request, str('Erro: Não foi possível consultar as variáveis com abrangencia: '+self.abrangencia_str(abrangencia)+'.'))
                return False
        except:
            messages.error(self.request, str('Erro: Não foi possível consultar as variáveis dos '+self.abrangencia_str(abrangencia)+' no Banco de Dados.'))
            return False
    
    def get_var_nome(self, qs, nome):
        try:
            variavel = qs.get(nome=nome)
            return variavel
        except:
            messages.error(self.request, str('Erro: Não foi possível encontrar nenhuma variável com o nome: '+str(nome)+' no Banco de Dados.'))
            return False
    
    def obter_especificacao_abrangencia(self, abrangencia, nome):
        try:
            if(abrangencia == 'PAIS'):
                return Pais.objects.get(nome_normalizado=nome)
            elif(abrangencia == 'ESTA'):
                return Estado.objects.get(nome_normalizado=nome)
            elif(abrangencia == 'MUNI'):
                return Municipio.objects.get(nome_normalizado=nome)
            else:
                messages.error(self.request, str('Erro: A abrangência: '+str(abrangencia)+' não é válida.'))
                return False
        except:
            messages.error(self.request, str('Erro: Não foi possível encontrar o '+self.abrangencia_str_atributo_model(abrangencia)+': '+str(nome)+' no Banco de Dados.'))
            return False
    
    def variavel_is_int(self, unidade):
        if(unidade == 'INTE' or unidade == 'SEMU'):
            return True
        return False
    
    def variavel_is_dec(self, unidade):
        if(unidade == 'DECI' or unidade == 'REAL' or unidade == 'DOLA' or unidade == 'EURO' or unidade == 'PORC'):
            return True
        return False
    
    def format_date(self, date):
        return _date(date,"d/m/Y")
    
    def atualizar_valor(self, linha_qs, abrangencia, espec_abr, data, variavel, valor):
        try:
            for entry in linha_qs:
                entry.valor = valor
                entry.save()
            self.c_geral += 1
            self.c_atualizacao +=1
            return 'S'
        except:
            messages.error(self.request, str('Erro: Não foi possível atualizar o valor do '+self.abrangencia_str_atributo_model(abrangencia)+': '+espec_abr.nome+'-'+' Variavel:'+variavel.nome+', Data:'+self.format_date(data)+', Valor:'+valor+' no Banco de Dados.'))
            return False
    
    def cadastrar_valor(self, nova_linha, abrangencia, espec_abr, data, variavel, valor):
        try:
            nova_linha.save()
            self.c_geral += 1
            self.c_cadastro += 1
            return 'S'
        except:
            messages.error(self.request, str('Erro: Não foi possível cadastrar o valor do '+self.abrangencia_str_atributo_model(abrangencia)+': '+espec_abr.nome+'-'+' Variavel:'+variavel.nome+', Data:'+self.format_date(data)+', Valor:'+valor+' no Banco de Dados.'))
            return False
    
    def atualizar_ou_cadastrar_linha(self, abrangencia, espec_abr, data, variavel, valor):
        try:
            if(abrangencia == 'PAIS'):
                if(self.variavel_is_int(variavel.unidade)):
                    linha_qs = VariavelPaisInteiro.objects.select_for_update().filter(variavel=variavel, data=data, pais=espec_abr)
                    if(linha_qs.count() == 1): #linha existe, atualizar valor
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelPaisInteiro(variavel=variavel, pais=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                elif(self.variavel_is_dec(variavel.unidade)):
                    linha_qs = VariavelPaisDecimal.objects.select_for_update().filter(variavel=variavel, pais=espec_abr, data=data)
                    if(linha_qs.count() == 1):
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelPaisDecimal(variavel=variavel, pais=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                else:
                    messages.error(self.request, str('Erro: A Unidade da variável: '+str(variavel.nome)+' não é válida.'))
                    return False
            elif(abrangencia == 'ESTA'):
                if(self.variavel_is_int(variavel.unidade)):
                    linha_qs = VariavelEstadoInteiro.objects.select_for_update().filter(variavel=variavel, data=data, estado=espec_abr)
                    if(linha_qs.count() == 1): #linha existe, atualizar valor
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelEstadoInteiro(variavel=variavel, estado=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                elif(self.variavel_is_dec(variavel.unidade)):
                    linha_qs = VariavelEstadoDecimal.objects.select_for_update().filter(variavel=variavel, estado=espec_abr, data=data)
                    if(linha_qs.count() == 1):
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelEstadoDecimal(variavel=variavel, estado=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                else:
                    messages.error(self.request, str('Erro: A Unidade da variável: '+str(variavel.nome)+' não é válida.'))
                    return False
            elif(abrangencia == 'MUNI'):
                if(self.variavel_is_int(variavel.unidade)):
                    linha_qs = VariavelMunicipioInteiro.objects.select_for_update().filter(variavel=variavel, data=data, municipio=espec_abr)
                    if(linha_qs.count() == 1): #linha existe, atualizar valor
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelMunicipioInteiro(variavel=variavel, municipio=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                elif(self.variavel_is_dec(variavel.unidade)):
                    linha_qs = VariavelMunicipioDecimal.objects.select_for_update().filter(variavel=variavel, municipio=espec_abr, data=data)
                    if(linha_qs.count() == 1):
                        resp = self.atualizar_valor(linha_qs, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                    else:
                        nova_linha = VariavelMunicipioDecimal(variavel=variavel, municipio=espec_abr, data=data, valor=valor)
                        resp = self.cadastrar_valor(nova_linha, abrangencia, espec_abr, data, variavel, valor)
                        if(resp is bool):
                            return False
                else:
                    messages.error(self.request, str('Erro: A Unidade da variável: '+str(variavel.nome)+' não é válida.'))
                    return False
            else:
                messages.error(self.request, str('Erro: A abrangência: '+str(abrangencia)+' não é válida.'))
                return False
        except:
            messages.error(self.request, str('Erro: Não foi possível processar os dados atuais: '+self.abrangencia_str_atributo_model(abrangencia)+': '+espec_abr.nome+'-'+' Variavel:'+variavel.nome+', Data:'+self.format_date(data)+', Valor:'+valor+'.'))
            return False
    
    @transaction.atomic
    def importar_xlsx(self, arquivo):
        c_geral = 0
        conteudo_arquivo = self.ler_arquivo(arquivo)
        if(conteudo_arquivo is bool): #se o retorno for False entao ocorreu um erro, que foi adicionado a lista messages da request
            return False
        controle = self.ler_tabela(conteudo_arquivo, 'Controle')
        if(controle is bool):
            return False
        abrangencia = self.obter_abrangencia_arq(controle)
        if(abrangencia is bool):
            return False
        lista_espec_abr = self.lista_especificacao_abrangencia(conteudo_arquivo, abrangencia)
        if(abrangencia is bool):
            return False
        vars_abr = self.obter_vars_abr(abrangencia)
        if(vars_abr is bool):
            return False
        
        try:
            with transaction.atomic():
                for i in lista_espec_abr.index:
                    nome_normalizado = self.valor_unico_lc(self.abrangencia_str(abrangencia), lista_espec_abr, i, 'Nome_Normalizado')
                    espec_abr = self.obter_especificacao_abrangencia(abrangencia, nome_normalizado)
                    if(espec_abr is bool):
                        return False
                    tabela = self.ler_tabela(conteudo_arquivo, nome_normalizado)
                    if(tabela is bool):
                        return False
                    tabela = self.replaceNaNWithNone(tabela)
                    for linha in tabela.index:
                        for coluna in tabela.columns:
                            if(coluna != 'Data' and coluna != 'Tempo/Variável' and 'Unamed' not in coluna):
                                var_atual = self.get_var_nome(vars_abr, coluna)
                                if(var_atual is bool):
                                    return False
                                data = self.valor_unico_lc(self.abrangencia_str(abrangencia), tabela, linha, 'Data')
                                if(data is bool):
                                    return False
                                if(data != None):
                                    valor = self.valor_unico_lc(self.abrangencia_str(abrangencia), tabela, linha, var_atual.nome)
                                    if(valor is bool):
                                        return False
                                    #print(data, var_atual, valor)
                                    resp = self.atualizar_ou_cadastrar_linha(abrangencia, espec_abr, data, var_atual, valor)
                                    if(resp is bool):
                                        return False
                        #print()
        except Error as e:
            messages.error(self.request,'Erro: Ocorreu um problema durante a gravação no Banco de Dados, voltando ao estado anterior ao envio do arquivo')
            messages.error(self.request, str('Descrição do Erro a ser informada ao administrador: '+str(e.getMessage())))
            self.c_geral = 0
            return False
        
        messages.success(self.request,'Dados dos '+self.abrangencia_str(abrangencia)+' atualizados com sucesso!')
        messages.info(self.request, str('Contagem de dados atualizados: Cadastros:'+str(self.c_cadastro)+', Atualizações:'+str(self.c_atualizacao)+', Total:'+str(self.c_geral)+'.'))
        return True

    @transaction.atomic
    def importar_municipios_rs_xlsx(self, arquivo):
        conteudo_arquivo = self.ler_arquivo(arquivo)
        if(conteudo_arquivo is bool):
            return False
        if(conteudo_arquivo is bool):
            return False
        dados = self.ler_tabela(conteudo_arquivo, 'Municipios')
        if(dados is bool):
            return False
        dados = self.replaceNaNWithNone(dados)
        if(dados is bool):
            return False
        linhas_tab = dados.index
        estado = self.obter_especificacao_abrangencia('ESTA','rio-grande-do-sul')
        if(estado is bool):
            return False
        u = 0
        a = 0
        try:
            with transaction.atomic():
                for linha_atual in linhas_tab:
                    nome = self.valor_unico_lc('Municipios', dados, linha_atual, 'nome')
                    nome_normalizado = self.valor_unico_lc('Municipios', dados, linha_atual, 'nome_normalizado')
                    codigo_ibge = self.valor_unico_lc('Municipios', dados, linha_atual, 'codigo_ibge')
                    numero_habitantes = self.valor_unico_lc('Municipios', dados, linha_atual, 'numero_habitantes')
                    total_de_repasse_programa_apoio_financeiro = self.valor_unico_lc('Municipios', dados, linha_atual, 'total_de_repasse_programa_apoio_financeiro')
                    municipio_existe = Municipio.objects.select_for_update().filter(estado=estado, nome_normalizado=nome_normalizado)
                    if(municipio_existe.count() == 1):
                        municipio_atual = Municipio.objects.get(estado=estado, nome_normalizado=nome_normalizado)
                        municipio_atual.codigo_ibge = codigo_ibge
                        municipio_atual.numero_habitantes = numero_habitantes
                        municipio_atual.total_de_repasse_programa_apoio_financeiro = total_de_repasse_programa_apoio_financeiro
                        try:
                            municipio_atual.save()
                            u += 1
                        except:
                            messages.error(self.request, str('Erro: Não foi possível atualizar os dados do município: '+nome+' no Banco de Dados.'))
                            return False
                    elif(municipio_existe.count() == 0):
                        l = Municipio(
                            estado = estado,
                            codigo_ibge = codigo_ibge,
                            nome = nome,
                            nome_normalizado = nome_normalizado,
                            numero_habitantes = numero_habitantes,
                            total_de_repasse_programa_apoio_financeiro = total_de_repasse_programa_apoio_financeiro
                        )
                        try:
                            l.save()
                            a += 1
                        except:
                            messages.error(self.request, str('Erro: Não foi possível cadastrar os dados do município: '+nome+' no Banco de Dados.'))
                            return False
                messages.info(self.request, str('Municípios atualizados: '+str(u)+', municípios cadastrados: '+str(a)+'.'))
                return True
        except:
            messages.error(self.request,'Erro: Ocorreu um problema durante a gravação do municípios no Banco de Dados, voltando ao estado anterior ao envio do arquivo')
            return False
