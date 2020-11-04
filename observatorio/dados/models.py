from django.db import models
from django.utils.text import slugify

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
    fonte = models.ForeignKey(Fonte, on_delete=models.CASCADE, blank=True)
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

class VariaveisGrafico(models.Model):
    grafico = models.ForeignKey(Grafico, on_delete=models.CASCADE)
    variavel = models.ForeignKey(Variavel, on_delete=models.CASCADE)
    ordem = models.IntegerField(default=0)

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
