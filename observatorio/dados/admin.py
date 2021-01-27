from django.contrib import admin
from .models import Continente, Pais, Estado, Municipio, Variavel, Fonte, Grafico, VariaveisGrafico, Integrante, TextoOficial, Documento, AutorDocumento, NoticiaExterna
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin

#admin.site.register(Continente)
#admin.site.register(Post)
class ContinenteResource(resources.ModelResource):
    class Meta:
        model = Continente

@admin.register(Continente)
class ContinenteAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id','nome', 'nome_normalizado')
    search_fields = ('nome',)
    #prepopulated_fileds = {'slug': ('nome',)}
    #raw_id_fields = ('author',)
    #date_hierarchy = 'publish'
    ordering = ('nome',)
    resource_class = ContinenteResource

class PaisResource(resources.ModelResource):
    class Meta:
        model = Pais

@admin.register(Pais)
class PaisAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado',)
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)
    resource_class = PaisResource

class EstadoResource(resources.ModelResource):
    class Meta:
        model = Estado

@admin.register(Estado)
class EstadoAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'sigla', 'codigo_ibge')
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)
    resource_class = EstadoResource

class FonteResource(resources.ModelResource):
    class Meta:
        model = Fonte

@admin.register(Fonte)
class FonteAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'url',)
    ordering = ('nome',)
    resource_class = FonteResource

class VariaveisGraficoInLine(admin.TabularInline):
    model = Grafico.variaveis.through
    extra = 1
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "variavel":
            #abrangencia_grafico_atual = list(Grafico.objects.filter(id=kwargs.get('id')))[0].abrangencia
            abrangencia_grafico_atual = request.get_full_path()
            vet_string_abrangencia = abrangencia_grafico_atual.split('/')
            grafico_id = vet_string_abrangencia[4]
            if grafico_id != 'add':
                abrangencia_opcao = list(Grafico.objects.filter(id=grafico_id))[0].abrangencia
                print(abrangencia_opcao)
                kwargs["queryset"] = Variavel.objects.filter(abrangencia=abrangencia_opcao)
            else:
                kwargs["queryset"] = Variavel.objects.all()[:0]
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # def get_queryset(self, request):
    #     qs = super(VariaveisGraficoInLine, self).get_queryset(request)
    #     qs = qs.filter(abrangencia='EST')
    #     return qs

class VariavelResource(resources.ModelResource):
    class Meta:
        model = Variavel

@admin.register(Variavel)
class VariavelAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'abrangencia', 'ativa', 'ordem', 'unidade', 'variavel_exclusiva_do_estado_RS', 'fonte',)
    ordering = ('nome',)
    list_filter = ('abrangencia', 'ativa', 'unidade',)
    resource_class = VariavelResource

class GraficoResource(resources.ModelResource):
    class Meta:
        model = Grafico

@admin.register(Grafico)
class GraficoAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'abrangencia', 'ativo', 'ordem',)
    ordering = ('nome',)
    inlines = [
        VariaveisGraficoInLine,
    ]
    list_filter = ('abrangencia', 'ativo',)
    resource_class = GraficoResource

class MunicipioResource(resources.ModelResource):
    class Meta:
        model = Municipio

@admin.register(Municipio)
class MunicipioAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'estado', 'codigo_ibge', 'numero_habitantes', 'total_de_repasse_programa_apoio_financeiro')
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)
    list_filter = ('estado',)
    resource_class = MunicipioResource

class IntegranteResource(resources.ModelResource):
    class Meta:
        model = Integrante

@admin.register(Integrante)
class IntegrantesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'instituicao', 'equipe', 'ordem')
    list_filter = ('equipe', )
    #ordering = ('nome',)
    resource_class = IntegranteResource

class TextoOficialResource(resources.ModelResource):
    class Meta:
        model = TextoOficial

@admin.register(TextoOficial)
class TextoOficialAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'titulo', 'data', 'descricao', 'pais', 'estado', 'url')
    #ordering = ('nome',)
    resource_class = TextoOficialResource

class AutoresDocumentoInLine(admin.TabularInline):
    model = Documento.autores.through
    extra = 1
    
class DocumentoResource(resources.ModelResource):
    class Meta:
        model = Documento

@admin.register(Documento)
class DocumentoAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'numero', 'titulo', 'data', 'tipo', 'arquivo', )
    ordering = ('-data',)
    inlines = [
        AutoresDocumentoInLine,
    ]
    list_filter = ('tipo', 'data',)
    resource_class = DocumentoResource
    
class NoticiaExternaResource(resources.ModelResource):
    class Meta:
        model = NoticiaExterna

@admin.register(NoticiaExterna)
class NoticiaExternaAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'tipo', 'titulo', 'fonte', 'url',)
    list_filter = ('tipo', 'fonte')
    resource_class = NoticiaExternaResource