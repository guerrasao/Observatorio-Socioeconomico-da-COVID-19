from django.db import models
from django.utils.text import slugify
from easy_thumbnails.fields import ThumbnailerField

#Abrangência
class Continente(models.Model):
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "continente"
        verbose_name_plural = "continentes"
    
    def __str__(self):
        return self.nome
    
    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Continente,self).save()

class Pais(models.Model):
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    continente = models.ForeignKey(Continente, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "país"
        verbose_name_plural = "países"
    
    def __str__(self):
        return self.nome

    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Pais,self).save()

class Estado(models.Model):
    codigo_ibge = models.IntegerField(blank=True, null=True, db_index=True)
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    sigla = models.CharField(max_length=3)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    
    def clean(self):
        self.sigla = str(self.sigla.upper())
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "estado"
        verbose_name_plural = "estados"
    
    def __str__(self):
        return self.nome

    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Estado,self).save()

class Municipio(models.Model):
    codigo_ibge = models.IntegerField(db_index=True)
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    numero_habitantes = models.IntegerField(blank=True, null=True)
    total_de_repasse_programa_apoio_financeiro = models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True)
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "município"
        verbose_name_plural = "municípios"
    
    def __str__(self):
        return self.nome

    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Municipio,self).save()

class Fonte(models.Model):
    nome = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "Fonte de Dados"
        verbose_name_plural = "Fontes de Dados"
    
    def __str__(self):
        return self.nome

#Modelo Padrão de Variável
class Variavel(models.Model):
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    ABRANGENCIA_VARIAVEL = [
        ('CONT', 'Continente'),
        ('PAIS', 'País'),
        ('ESTA', 'Estado'),
        ('MUNI', 'Município'),
    ]
    abrangencia = models.CharField(max_length=4, choices=ABRANGENCIA_VARIAVEL)
    ativa = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    fonte = models.ForeignKey(Fonte, on_delete=models.CASCADE, blank=True, null=True)
    UNIDADES_VARIAVEL=[
        ('SEMU', 'Sem Unidade'),
        ('INTE', 'Inteiro'),
        ('DECI', 'Decimal'),
        ('REAL', 'Moeda (Real)'),
        ('DOLA', 'Moeda (Dolar)'),
        ('EURO', 'Moeda (Euro)'),
        ('PORC', 'Porcentagem'),
    ]
    unidade = models.CharField(max_length=4, choices=UNIDADES_VARIAVEL, blank=True)
    variavel_exclusiva_do_estado_RS = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "variável"
        verbose_name_plural = "variáveis"
    
    def __str__(self):
        return self.nome
    
    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Variavel,self).save()

class Grafico(models.Model):
    nome = models.CharField(max_length=255)
    nome_normalizado = models.SlugField(max_length=255, editable=False)
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    abrangencia = models.CharField(max_length=4, choices=Variavel.ABRANGENCIA_VARIAVEL)
    TIPO_GRAFICO = [
        ('LINH', 'Linhas'),
        ('BARR', 'Barras'),
    ]
    tipo = models.CharField(max_length=4, choices=TIPO_GRAFICO, blank=True)
    variaveis = models.ManyToManyField(Variavel, through='VariaveisGrafico', related_name="variaveis_do_grafico")
    
    class Meta:
        ordering = ('nome',)
        verbose_name = "Gráfico"
        verbose_name_plural = "Gráficos"
    
    def save(self):
        self.nome_normalizado = slugify(self.nome)
        super(Grafico,self).save()
    
    def __str__(self):
        return self.nome

class VariaveisGrafico(models.Model):
    grafico = models.ForeignKey(Grafico, on_delete=models.CASCADE)
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    ordem = models.IntegerField(default=0)
    
    def __str__(self):
        return 'Variável: '+self.variavel.nome

    class Meta:
        verbose_name = "variável do gráfico"
        verbose_name_plural = "variáveis do gráfico"
        unique_together = (("grafico", "variavel"),)

#Padrão de Variável Conforme Abrangência, sem campo valor, apenas as chaves
#Implementação sem classes/tipos genéricas(os)
class VariavelContinente(models.Model):
    chave = models.UniqueConstraint(fields=['variavel','continente','data'], name='pk_variavel_continente_data')
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    continente = models.ForeignKey(Continente, on_delete=models.CASCADE)
    data = models.DateField(db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ['variavel','continente','data']

class VariavelPais(models.Model):
    chave = models.UniqueConstraint(fields=['variavel','pais','data'], name='pk_variavel_pais_data')
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    data = models.DateField(db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        unique_together = ['variavel','pais','data']

class VariavelEstado(models.Model):
    chave = models.UniqueConstraint(fields=['variavel','estado','data'], name='pk_variavel_estado_data')
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    data = models.DateField(db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        unique_together = ['variavel','estado','data']

class VariavelMunicipio(models.Model):
    chave = models.UniqueConstraint(fields=['variavel','municipio','data'], name='pk_variavel_municipio_data')
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    data = models.DateField(db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        unique_together = ['variavel','municipio','data']

#Padrão do campo valor, conforme tipo de dado e abrangência
#Implementação sem classes/tipos genéricas(os)

#Continente
class VariavelContinenteInteiro(VariavelContinente):  
    valor = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = False

class VariavelContinenteDecimal(VariavelContinente):
    valor = models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True)
    class Meta:
        abstract = False

#Pais
class VariavelPaisInteiro(VariavelPais):
    valor = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = False

class VariavelPaisDecimal(VariavelPais):
    valor = models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True)
    class Meta:
        abstract = False

#Estado
class VariavelEstadoInteiro(VariavelEstado):
    valor = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = False

class VariavelEstadoDecimal(VariavelEstado):
    valor = models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True)
    class Meta:
        abstract = False

#Municipio
class VariavelMunicipioInteiro(VariavelMunicipio):
    valor = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = False

class VariavelMunicipioDecimal(VariavelMunicipio):
    valor = models.DecimalField(blank=True, decimal_places=10, max_digits=25, null=True)
    class Meta:
        abstract = False

class Integrante(models.Model):
    nome = models.CharField(max_length=255)
    instituicao = models.CharField(max_length=255, null=True, blank=True, verbose_name='Instituição')
    SELECAO_EQUIPE = [
        ('COOR', 'Coordenação'),
        ('EXEC', 'Equipe Executiva'),
        ('OPER', 'Equipe Operacional'),
        ('APOI', 'Estrutura Apoiadora'),
        ('COLA', 'Equipe Colaborativa'),
        ('FINA', 'Estrutura Financiadora'),
    ]
    equipe = models.CharField(max_length=4, choices=SELECAO_EQUIPE)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('nome', 'ordem', )
        verbose_name = "Integrante"
        verbose_name_plural = "Integrantes"
        
    def __str__(self):
        return self.nome

class TextoOficial(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Título')
    data = models.DateField(db_index=True)
    descricao = models.CharField(max_length=2000, verbose_name='Descrição', null=True, blank=True)
    url = models.URLField(blank=True, max_length=1000)
    pais = models.ForeignKey(Pais, null=True, blank = True, on_delete=models.SET_NULL)
    estado = models.ForeignKey(Estado, null=True, blank = True, on_delete=models.SET_NULL)
    
    class Meta:
        ordering = ('-data', )
        verbose_name = "Texto Oficial"
        verbose_name_plural = "Textos Oficiais"
        
    def __str__(self):
        return self.titulo

class Documento(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Título')
    data = models.DateField(db_index=True)
    TIPO_DOCUMENTO = [
        ('CONJ', 'Análise de Conjuntura'),
        ('DISC', 'Texto para Discussão'),
    ]
    tipo = models.CharField(max_length=4, choices=TIPO_DOCUMENTO, blank=True)
    autores = models.ManyToManyField(Integrante, through='AutorDocumento', related_name="autores_do_documento")
    arquivo = ThumbnailerField(upload_to ='documents/%Y/%m/%d/')
    numero = models.IntegerField(default=0, verbose_name='Número')
    
    class Meta:
        ordering = ('-data', )
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
    
    def __str__(self):
        return self.titulo
    
    def save(self):
        if(self.numero == 0):
            self.numero = (Documento.objects.all().filter(tipo=self.tipo).count())+1
        super(Documento,self).save()

class AutorDocumento(models.Model):
    documento = models.ForeignKey(Documento, null=True, blank = True, on_delete=models.SET_NULL)
    autor = models.ForeignKey(Integrante, null=True, blank = True, on_delete=models.SET_NULL)
    ordem = models.IntegerField(default=0)

    def __str__(self):
        return 'Autor: '+self.autor.nome

    class Meta:
        ordering = ('ordem', )
        verbose_name = "autor do documento"
        verbose_name_plural = "autores do documento"
        unique_together = (("documento", "autor"),)

class NoticiaExterna(models.Model):
    titulo = models.CharField(max_length=1000, verbose_name='Título')
    url = models.URLField(blank=True, max_length=1000)
    fonte = models.CharField(max_length=255, blank=True)
    TIPO_NOTICIA_EXTERNA = [
        ('CRIA', 'Criação'),
        ('NOTI', 'Notícia de Opinião e Entrevistas'),
        ('LIVE', 'Lives'),
    ]
    tipo = models.CharField(max_length=4, choices=TIPO_NOTICIA_EXTERNA, blank=True)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('-id', )
        verbose_name = "Notícia Externa"
        verbose_name_plural = "Notícias Externas"