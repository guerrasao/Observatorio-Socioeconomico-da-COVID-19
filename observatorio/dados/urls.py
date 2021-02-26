from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='pagina_inicial'),
    path('importar/importar_dados', views.importar_dados, name='importar_dados'),
    path('importar/importar_municipios_rs', views.importar_municipios_rs, name='importar_municipios_rs'),
    path('dados/pais/<slug:pais>/tabelas', views.tabelas_pais, name='pais_tabelas'),
    path('dados/pais/<slug:pais>', views.graficos_pais, name='pais_graficos'),
    path('dados/estados', views.estados, name='estados'),
    path('dados/estado/<slug:estado>', views.estado, name='estado'),
    path('dados/municipios', views.municipios, name='municipios'),
    path('dados/municipio/<slug:municipio>', views.municipio, name='municipio'),
    #path('dados/estado/<slug:estado>/tabelas', views.tabelas_estado, name='estado_tabelas'),
    path('dados/', views.dados, name='dados'),
    # path('pais/<slug:pais>/estado/<slug:estado>', views.estado, name='estado'),
    # path('pais/<slug:pais>/estado/<slug:estado>/municipio/<int:municipio>', views.municipío, name='municipio'),
    
    #path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
]