from django.urls import path
from . import views

app_name = 'resultats'

urlpatterns = [
    path('rdv-du-jour/', views.rdv_du_jour, name='rdv_du_jour'),
    path('valider-presence/<int:rdv_id>/', views.valider_presence, name='valider_presence'),
    path('saisir/<int:rdv_id>/', views.saisir_resultat, name='saisir_resultat'),
    path('rapport/<int:periode_id>/', views.rapport_general, name='rapport_general'),
    path('etudiant/<int:resultat_id>/', views.detail_resultat_etudiant, name='detail_etudiant'),
]