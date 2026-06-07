from django.urls import path
from . import views

app_name = 'periodes'

urlpatterns = [
    path('',                          views.liste_periodes,    name='liste'),
    path('creer/',                    views.creer_periode,     name='creer'),
    path('<int:pk>/',                 views.detail_periode,    name='detail'),
    path('<int:pk>/modifier/',        views.modifier_periode,  name='modifier'),
    path('<int:pk>/supprimer/',       views.supprimer_periode, name='supprimer'),
    path('<int:pk>/statut/',          views.changer_statut,    name='statut'),
    path('<int:pk>/importer-csv/',    views.importer_csv,      name='importer_csv'),
]