from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='pagina_inicial'),
    path('dados/pais/<slug:pais>/tabelas', views.tabelas_pais, name='pais_tabelas'),
    path('dados/pais/<slug:pais>', views.graficos_pais, name='pais_graficos'),
    path('dados/estados', views.estados, name='estados'),
    path('dados/estados/ranking', views.rank_estados, name='rank_estados'),
    path('dados/estados/ranking-mensal', views.rank_estados_mensal, name='rank_estados_mensal'),
    path('dados/estado/<slug:estado>/tabelas', views.tabelas_estado, name='estado_tabelas'),
    path('dados/estado/<slug:estado>', views.estado, name='estado'),
    path('dados/municipios', views.municipios, name='municipios'),
    path('dados/municipios/ranking', views.rank_municipios, name='rank_municipios'),
    path('dados/municipios/ranking-mensal', views.rank_municipios_mensal, name='rank_municipios_mensal'),
    path('dados/municipio/<slug:municipio>/tabelas', views.tabelas_municipio, name='municipio_tabelas'),
    path('dados/municipio/<slug:municipio>', views.municipio, name='municipio'),
    path('dados/', views.dados, name='dados'),
    path('equipe/', views.equipe, name='equipe'),
    path('analises-de-conjuntura/', views.analises_de_conjuntura, name='analises_de_conjuntura'),
    path('textos-para-discussao/', views.textos_para_discussao, name='textos_para_discussao'),
    path('textos-oficiais/pais/<slug:pais>/', views.textos_oficiais_abr_pais, name='textos_oficiais_pais'),
    path('textos-oficiais/estado/<slug:estado>/', views.textos_oficiais_abr_estado, name='textos_oficiais_estado'),
    path('textos-oficiais/', views.textos_oficiais, name='textos_oficiais'),
    #path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
]