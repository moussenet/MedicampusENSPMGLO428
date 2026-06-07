from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, CodeValidationENSPM
from .forms import EtudiantRegisterForm, LoginForm, CreateStaffForm, ChangePasswordForm


# ─── Page d'accueil → redirige vers login ───────────────────────────────────
def home(request):
    return redirect('accounts:login')


# ─── Inscription étudiant ────────────────────────────────────────────────────
def register_etudiant(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = EtudiantRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='accounts.backends.EmailBackend')
        messages.success(request, 'Compte créé avec succès. Bienvenue !')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html', {'form': form})


# ─── Login ───────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Votre compte est désactivé. Contactez l\'administration.')
            else:
                login(request, user)
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'accounts/login.html', {'form': form})


# ─── Logout ──────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ─── Dashboard — redirige selon le rôle ─────────────────────────────────────
@login_required
def dashboard(request):
    role = request.user.role
    if role == 'superadmin':
        return redirect('accounts:superadmin_dashboard')
    elif role == 'admin':
        return redirect('accounts:admin_dashboard')
    elif role == 'medecin':
        return redirect('accounts:medecin_dashboard')
    else:
        return redirect('accounts:etudiant_dashboard')


# ─── Dashboard super-admin ───────────────────────────────────────────────────
@login_required
def superadmin_dashboard(request):
    if not request.user.is_superadmin:
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    admins   = User.objects.filter(role='admin').order_by('-date_joined')
    medecins = User.objects.filter(role='medecin').order_by('-date_joined')
    codes    = CodeValidationENSPM.objects.filter(est_utilise=False).order_by('-created_at')

    return render(request, 'accounts/superadmin_dashboard.html', {
        'admins':   admins,
        'medecins': medecins,
        'codes':    codes,
    })


# ─── Créer admin ou médecin ──────────────────────────────────────────────────
@login_required
def create_staff(request):
    if not request.user.is_superadmin:
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    form = CreateStaffForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(created_by=request.user)
        role_label = dict(form.fields['role'].choices)[form.cleaned_data['role']]
        messages.success(request, f'Compte {role_label} créé avec succès.')
        return redirect('accounts:superadmin_dashboard')

    return render(request, 'accounts/create_staff.html', {'form': form})


# ─── Activer / Désactiver un compte ─────────────────────────────────────────
@login_required
def toggle_account(request, user_id):
    if not request.user.is_superadmin:
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    user = get_object_or_404(User, id=user_id, role__in=['admin', 'medecin'])
    user.is_active = not user.is_active
    user.save()
    etat = 'activé' if user.is_active else 'désactivé'
    messages.success(request, f'Compte de {user.get_display_name()} {etat}.')
    return redirect('accounts:superadmin_dashboard')


# ─── Supprimer définitivement un compte ─────────────────────────────────────
@login_required
def delete_account(request, user_id):
    if not request.user.is_superadmin:
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    user = get_object_or_404(User, id=user_id, role__in=['admin', 'medecin'])
    nom  = user.get_display_name()
    user.delete()
    messages.success(request, f'Compte de {nom} supprimé définitivement.')
    return redirect('accounts:superadmin_dashboard')


# ─── Générer un code ENSPM ───────────────────────────────────────────────────
@login_required
def generate_code(request):
    if not request.user.is_superadmin:
        messages.error(request, 'Accès refusé.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        import secrets, string
        alphabet = string.ascii_uppercase + string.digits
        code_str = 'ENSPM-' + ''.join(secrets.choice(alphabet) for _ in range(8))
        CodeValidationENSPM.objects.create(code=code_str, cree_par=request.user)
        messages.success(request, f'Code généré : {code_str}')

    return redirect('accounts:superadmin_dashboard')


# ─── Dashboards secondaires (à développer) ──────────────────────────────────
@login_required
def admin_dashboard(request):
    from periodes.models import PeriodeVisite
    from rendezvous.models import RendezVous
    from resultats.models import RapportMedical, ResultatMedical

    periodes = PeriodeVisite.objects.all().order_by('-date_debut')[:5]

    nb_periodes_actives = PeriodeVisite.objects.filter(statut__in=['programmee', 'en_cours']).count()
    nb_rdv_total        = RendezVous.objects.count()
    nb_presents         = RendezVous.objects.filter(statut='present').count()
    nb_absents          = RendezVous.objects.filter(statut='absent').count()
    nb_aptes            = ResultatMedical.objects.filter(statut_aptitude='apte').count()
    nb_inaptes          = ResultatMedical.objects.filter(statut_aptitude__in=['inapte', 'inapte_temporaire']).count()

    rapports = RapportMedical.objects.select_related('medecin', 'periode').order_by('-created_at')[:5]

    return render(request, 'accounts/admin_dashboard.html', {
        'periodes':            periodes,
        'nb_periodes_actives': nb_periodes_actives,
        'nb_rdv_total':        nb_rdv_total,
        'nb_presents':         nb_presents,
        'nb_absents':          nb_absents,
        'nb_aptes':            nb_aptes,
        'nb_inaptes':          nb_inaptes,
        'rapports':            rapports,
    })

@login_required
def medecin_dashboard(request):
    from django.utils import timezone
    from rendezvous.models import RendezVous
    from resultats.models import RapportMedical
    from periodes.models import PeriodeVisite

    aujourd_hui = timezone.localdate()

    print(f"=== MEDECIN ID: {request.user.id} ===")
    print(f"=== AUJOURD'HUI: {aujourd_hui} ===")

    rdvs_jour = RendezVous.objects.filter(
        creneau__date=aujourd_hui,
        creneau__periode__medecin=request.user,
    ).select_related('etudiant', 'creneau', 'creneau__periode').order_by('creneau__heure_debut')

    print(f"=== RDV TROUVES: {rdvs_jour.count()} ===")
    print(f"=== QUERY: {rdvs_jour.query} ===")

    periodes_actives = PeriodeVisite.objects.filter(
        medecin=request.user,
        statut__in=['programmee', 'en_cours'],
    ).order_by('date_debut')

    rapports = RapportMedical.objects.filter(
        medecin=request.user
    ).order_by('-created_at')[:5]

    return render(request, 'accounts/medecin_dashboard.html', {
        'rdvs_jour':       rdvs_jour,
        'aujourd_hui':     aujourd_hui,
        'periodes_actives': periodes_actives,
        'rapports':        rapports,
    })

@login_required
def etudiant_dashboard(request):
    from rendezvous.models import RendezVous
    from notifications.models import Notification
    from resultats.models import ResultatMedical

    rdvs = RendezVous.objects.filter(
        etudiant=request.user,
    ).select_related('creneau', 'creneau__periode').order_by('-creneau__date')[:5]

    notifications = Notification.objects.filter(
        user=request.user,
        archivee=False,
    ).order_by('-created_at')[:5]

    resultats = ResultatMedical.objects.filter(
        etudiant=request.user,
    ).order_by('-created_at')[:5]

    nb_non_lues = Notification.objects.filter(user=request.user, lu=False).count()

    return render(request, 'accounts/etudiant_dashboard.html', {
        'rdvs':        rdvs,
        'notifications': notifications,
        'resultats':   resultats,
        'nb_non_lues': nb_non_lues,
    })
# ─── Changement de mot de passe ─────────────────────────────────────────────
@login_required
def change_password(request):
    form = ChangePasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = request.user
        if not user.check_password(form.cleaned_data['ancien_password']):
            messages.error(request, 'Ancien mot de passe incorrect.')
        else:
            user.set_password(form.cleaned_data['nouveau_password'])
            user.save()
            login(request, user, backend='accounts.backends.EmailBackend')
            messages.success(request, 'Mot de passe modifié avec succès.')
            return redirect('accounts:dashboard')

    return render(request, 'accounts/change_password.html', {'form': form})