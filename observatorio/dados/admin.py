from django.contrib import admin
from .models import Continente, Pais, Estado, Municipio, Variavel, Fonte, Grafico, VariaveisGrafico, Integrante, TextoOficial, Documento, AutorDocumento, NoticiaExterna, VariavelPaisInteiro, VariavelPaisDecimal, VariavelEstadoInteiro, VariavelEstadoDecimal, VariavelMunicipioInteiro, VariavelMunicipioDecimal
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
    search_fields = ('id','nome','nome_normalizado',)
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
    search_fields = ('id', 'nome', 'nome_normalizado',)
    resource_class = PaisResource

class EstadoResource(resources.ModelResource):
    class Meta:
        model = Estado

@admin.register(Estado)
class EstadoAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'sigla', 'codigo_ibge')
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)
    search_fields = ('id', 'nome', 'nome_normalizado', 'sigla', 'codigo_ibge')
    resource_class = EstadoResource

class FonteResource(resources.ModelResource):
    class Meta:
        model = Fonte

@admin.register(Fonte)
class FonteAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'url',)
    ordering = ('nome',)
    search_fields = ('id', 'nome', 'url',)
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
                if(abrangencia_opcao == 'ESRS'):
                    kwargs["queryset"] = Variavel.objects.filter(abrangencia='ESTA', ativa=True)
                elif(abrangencia_opcao == 'ESTA'):
                    kwargs["queryset"] = Variavel.objects.filter(abrangencia=abrangencia_opcao, ativa=True, variavel_exclusiva_do_estado_RS=False)
                #print(abrangencia_opcao)
                else:
                    kwargs["queryset"] = Variavel.objects.filter(abrangencia=abrangencia_opcao, ativa=True)
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
    list_filter = ('abrangencia', 'ativa', 'unidade', 'variavel_exclusiva_do_estado_RS', 'fonte',)
    search_fields = ('nome','abrangencia','nome_normalizado','fonte__nome',)
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
    search_fields = ('id','nome','nome_normalizado','abrangencia','ordem',)
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
    search_fields = ('id','nome','nome_normalizado','codigo_ibge',)
    resource_class = MunicipioResource

class IntegranteResource(resources.ModelResource):
    class Meta:
        model = Integrante

@admin.register(Integrante)
class IntegrantesAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'instituicao', 'equipe', 'ordem')
    list_filter = ('equipe', 'instituicao')
    search_fields = ('id', 'nome', 'instituicao', 'equipe', 'ordem')
    #ordering = ('nome',)
    resource_class = IntegranteResource

class TextoOficialResource(resources.ModelResource):
    class Meta:
        model = TextoOficial

@admin.register(TextoOficial)
class TextoOficialAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'titulo', 'data', 'descricao', 'pais', 'estado', 'url')
    #ordering = ('nome',)
    list_filter = ('pais', 'estado')
    search_fields = ('id', 'titulo', 'data', 'descricao', 'pais__nome', 'estado__nome', 'url')
    resource_class = TextoOficialResource

class AutoresDocumentoInLine(admin.TabularInline):
    model = Documento.autores.through
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "autor":
            kwargs["queryset"] = Integrante.objects.filter(equipe__in=['COOR','EXEC','OPER','COLA'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    search_fields = ('id', 'numero', 'titulo', 'data', 'arquivo', )
    resource_class = DocumentoResource
    
class NoticiaExternaResource(resources.ModelResource):
    class Meta:
        model = NoticiaExterna

@admin.register(NoticiaExterna)
class NoticiaExternaAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'tipo', 'titulo', 'fonte', 'url',)
    list_filter = ('tipo', 'fonte')
    search_fields = ('id', 'tipo', 'titulo', 'fonte', 'url',)
    resource_class = NoticiaExternaResource

class VariavelPaisInteiroResource(resources.ModelResource):
    class Meta:
        model = VariavelPaisInteiro

@admin.register(VariavelPaisInteiro)
class VariavelPaisInteiroAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'pais', 'data', 'atualizado_em', )
    list_filter = ('pais',)
    search_fields = ('id', 'variavel__nome', 'pais__nome', 'data', 'atualizado_em',)
    resource_class = VariavelPaisInteiroResource
    def has_add_permission(self, request, obj=None):
        return False

class VariavelPaisDecimalResource(resources.ModelResource):
    class Meta:
        model = VariavelPaisDecimal

@admin.register(VariavelPaisDecimal)
class VariavelPaisDecimalAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'pais', 'data', 'atualizado_em', )
    list_filter = ('pais',)
    search_fields = ('id', 'variavel__nome', 'pais__nome', 'data', 'atualizado_em',)
    resource_class = VariavelPaisDecimalResource
    def has_add_permission(self, request, obj=None):
        return False

class VariavelEstadoInteiroResource(resources.ModelResource):
    class Meta:
        model = VariavelEstadoInteiro

@admin.register(VariavelEstadoInteiro)
class VariavelEstadoInteiroAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'estado', 'data', 'atualizado_em', )
    list_filter = ('estado',)
    search_fields = ('id', 'variavel__nome', 'estado__nome', 'data', 'atualizado_em',)
    resource_class = VariavelEstadoInteiroResource
    def has_add_permission(self, request, obj=None):
        return False

class VariavelEstadoDecimalResource(resources.ModelResource):
    class Meta:
        model = VariavelEstadoDecimal

@admin.register(VariavelEstadoDecimal)
class VariavelEstadoDecimalAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'estado', 'data', 'atualizado_em', )
    list_filter = ('estado',)
    search_fields = ('id', 'variavel__nome', 'estado__nome', 'data', 'atualizado_em',)
    resource_class = VariavelEstadoDecimalResource
    def has_add_permission(self, request, obj=None):
        return False

class VariavelMunicipioInteiroResource(resources.ModelResource):
    class Meta:
        model = VariavelMunicipioInteiro

@admin.register(VariavelMunicipioInteiro)
class VariavelMunicipioInteiroAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'municipio', 'data', 'atualizado_em', )
    list_filter = ('municipio',)
    search_fields = ('id', 'variavel__nome', 'municipio__nome', 'data', 'atualizado_em',)
    resource_class = VariavelMunicipioInteiroResource
    def has_add_permission(self, request, obj=None):
        return False

class VariavelMunicipioDecimalResource(resources.ModelResource):
    class Meta:
        model = VariavelMunicipioDecimal

@admin.register(VariavelMunicipioDecimal)
class VariavelMunicipioDecimalAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'variavel', 'valor', 'municipio', 'data', 'atualizado_em', )
    list_filter = ('municipio',)
    search_fields = ('id', 'variavel__nome', 'municipio__nome', 'data', 'atualizado_em',)
    resource_class = VariavelEstadoDecimalResource
    def has_add_permission(self, request, obj=None):
        return False