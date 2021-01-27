from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicial),
    path('pagina-inicial/', views.index, name='pagina_inicial'),
    path('importar/importar_dados', views.importar_dados, name='importar_dados'),
    path('importar/importar_municipios_rs', views.importar_municipios_rs, name='importar_municipios_rs'),
    path('dados/', views.dados, name='dados'),
    #path('paises/', views.paises, name='paises'),
    # path('pais/<slug:pais>', views.pais, name='pais'),
    # path('pais/<slug:pais>/estado/<slug:estado>', views.estado, name='estado'),
    # path('pais/<slug:pais>/estado/<slug:estado>/municipio/<int:municipio>', views.municipío, name='municipio'),
    
    #path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
]