from django.contrib import admin

# Register your models here.
from .models import Continente, Pais, Estado, Municipio, Variavel, Fonte, Grafico, VariaveisGrafico

#admin.site.register(Continente)
#admin.site.register(Post)
@admin.register(Continente)
class ContinenteAdmin(admin.ModelAdmin):
    list_display = ('id','nome', 'nome_normalizado')
    search_fields = ('nome',)
    #prepopulated_fileds = {'slug': ('nome',)}
    #raw_id_fields = ('author',)
    #date_hierarchy = 'publish'
    ordering = ('nome',)

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado',)
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'sigla', 'codigo_ibge')
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'estado', 'codigo_ibge')
    #prepopulated_fileds = {'nome_normalizado': ('nome',)}
    ordering = ('nome',)
    list_filter = ('estado',)

@admin.register(Fonte)
class FonteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'url',)
    ordering = ('nome',)

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

@admin.register(Variavel)
class VariavelAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'abrangencia', 'ativa', 'ordem', 'unidade', 'fonte',)
    ordering = ('nome',)
    list_filter = ('abrangencia', 'ativa', 'unidade',)

@admin.register(Grafico)
class GraficoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'nome_normalizado', 'abrangencia', 'ativo', 'ordem',)
    ordering = ('nome',)
    inlines = [
        VariaveisGraficoInLine,
    ]
    list_filter = ('abrangencia', 'ativo',)

#@admin.register(VariaveisGrafico)
#class VariaveisGraficoAdmin(admin.ModelAdmin):
#    list_display = ('id', 'grafico', 'variavel', 'ordem')
#    ordering = ('grafico',)