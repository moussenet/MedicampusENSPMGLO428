from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',                    views.home,                  name='home'),
    path('login/',              views.login_view,            name='login'),
    path('logout/',             views.logout_view,           name='logout'),
    path('register/',           views.register_etudiant,     name='register'),
    path('dashboard/',          views.dashboard,             name='dashboard'),

    # Super-admin
    path('superadmin/',         views.superadmin_dashboard,  name='superadmin_dashboard'),
    path('superadmin/create/',  views.create_staff,          name='create_staff'),
    path('superadmin/toggle/<int:user_id>/', views.toggle_account, name='toggle_account'),
    path('superadmin/delete/<int:user_id>/', views.delete_account, name='delete_account'),
    path('superadmin/generate-code/',        views.generate_code,  name='generate_code'),

    # Dashboards
    path('admin-dashboard/',    views.admin_dashboard,       name='admin_dashboard'),
    path('medecin-dashboard/',  views.medecin_dashboard,     name='medecin_dashboard'),
    path('etudiant-dashboard/', views.etudiant_dashboard,    name='etudiant_dashboard'),

    # Mot de passe
    path('change-password/',    views.change_password,       name='change_password'),
]