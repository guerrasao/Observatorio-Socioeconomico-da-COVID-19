from django.urls import path

from . import views

urlpatterns = [
    path('importar', views.importar_dados, name='importar_dados'),
    path('importar_municipios_rs', views.importar_municipios_rs, name='importar_municipios_rs'),
]