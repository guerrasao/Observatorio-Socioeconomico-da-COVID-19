"""observatorio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from dados.sitemaps import StaticViewSitemap, EstadoViewSitemap, PaisViewSitemap, AnaliseDeConjunturaViewSitemap, TextoParaDiscussaoViewSitemap, MunicipioViewSitemap
from django.conf import settings
from django.conf.urls.static import static
from dados import views

sitemaps = {
    'static' : StaticViewSitemap,
    'paises' : PaisViewSitemap,
    'estados' : EstadoViewSitemap,
    'municipios' : MunicipioViewSitemap,
    'analises-de-conjuntura' : AnaliseDeConjunturaViewSitemap,
    'textos-para-discussao' : TextoParaDiscussaoViewSitemap,
}

urlpatterns = [
    path('admin/dashboard/', views.contagem_dados, name='dashboard'),
    path('admin/importar_dados', views.importar_dados, name='importar_dados'),
    path('admin/importar_municipios_rs', views.importar_municipios_rs, name='importar_municipios_rs'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('dados.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Observatório Socieconômico da COVID-19 UFSM'                    # default: "Django Administration"
#admin.site.index_title = 'Features area'                 # default: "Site administration"
admin.site.site_title = 'OSE Admin' # default: "Django site admin"