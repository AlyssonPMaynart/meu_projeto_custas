from django.urls import path
from . import views

urlpatterns = [
    path('', views.escolha_recurso_view, name='escolha_recurso'),
    path('calcular/<str:tipo_recurso>/', views.calcular_custas_view, name='calcular_custas'),
]