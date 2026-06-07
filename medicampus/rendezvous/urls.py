from django.urls import path
from . import views

app_name = 'rendezvous'

urlpatterns = [
    path('periodes/', views.periodes_disponibles, name='periodes_disponibles'),
    path('prendre/<int:creneau_id>/', views.prendre_rdv, name='prendre_rdv'),
    path('annuler/<int:rdv_id>/', views.annuler_rdv, name='annuler_rdv'),
    path('mes-rdv/', views.mes_rendezvous, name='mes_rendezvous'),
]