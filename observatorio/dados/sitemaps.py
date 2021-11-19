from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Estado, Pais, Documento, Municipio
class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'
    def items(self):
        return ['pagina_inicial','dados','estados','rank_estados','rank_municipios','municipios','equipe','textos_oficiais']
    def location(self, item):
        return reverse(item)

class MunicipioViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    protocol = 'https'
    def items(self):
        return Municipio.objects.filter(estado__nome_normalizado='rio-grande-do-sul')

class EstadoViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    protocol = 'https'
    def items(self):
        return Estado.objects.filter(pais__nome_normalizado='brasil')

class PaisViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    protocol = 'https'
    def items(self):
        return Pais.objects.filter(continente__nome_normalizado='america-do-sul')

class AnaliseDeConjunturaViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'
    protocol = 'https'
    def items(self):
        return Documento.objects.filter(tipo='CONJ')
    
    def lastmod(self, obj):
        return obj.data

class TextoParaDiscussaoViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'
    protocol = 'https'
    def items(self):
        return Documento.objects.filter(tipo='DISC')
    
    def lastmod(self, obj):
        return obj.data

