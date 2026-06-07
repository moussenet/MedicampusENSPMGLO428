from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PeriodeVisite, EtudiantImporte
from .forms import PeriodeVisiteForm, ImportCSVForm
from accounts.models import User


def admin_requis(view_func):
    """Décorateur : réserve la vue aux admins et superadmins."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ['admin', 'superadmin']:
            messages.error(request, 'Accès réservé aux administrateurs.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Liste des périodes ──────────────────────────────────────────────────────
@admin_requis
def liste_periodes(request):
    periodes = PeriodeVisite.objects.all().order_by('-date_debut')
    return render(request, 'periodes/liste.html', {'periodes': periodes})


# ─── Créer une période ───────────────────────────────────────────────────────
@admin_requis
def creer_periode(request):
    form = PeriodeVisiteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        periode = form.save(commit=False)
        periode.cree_par = request.user
        periode.save()
        periode.generer_creneaux()
        nb = periode.creneaux.count()
        messages.success(
            request,
            f'Période créée avec succès. {nb} créneaux générés automatiquement.'
        )
        return redirect('periodes:detail', pk=periode.pk)
    return render(request, 'periodes/form.html', {'form': form, 'titre': 'Nouvelle période'})


# ─── Détail d'une période ────────────────────────────────────────────────────
@admin_requis
def detail_periode(request, pk):
    periode  = get_object_or_404(PeriodeVisite, pk=pk)
    creneaux = periode.creneaux.all().order_by('date', 'heure_debut')
    etudiants = periode.etudiants_importes.all()
    return render(request, 'periodes/detail.html', {
        'periode':   periode,
        'creneaux':  creneaux,
        'etudiants': etudiants,
    })


# ─── Modifier une période ────────────────────────────────────────────────────
@admin_requis
def modifier_periode(request, pk):
    periode = get_object_or_404(PeriodeVisite, pk=pk)
    form = PeriodeVisiteForm(request.POST or None, instance=periode)
    if request.method == 'POST' and form.is_valid():
        form.save()
        periode.generer_creneaux()
        messages.success(request, 'Période mise à jour. Les créneaux ont été régénérés.')
        return redirect('periodes:detail', pk=periode.pk)
    return render(request, 'periodes/form.html', {
        'form':  form,
        'titre': f'Modifier — {periode.titre}'
    })


# ─── Supprimer une période ───────────────────────────────────────────────────
@admin_requis
def supprimer_periode(request, pk):
    periode = get_object_or_404(PeriodeVisite, pk=pk)
    if request.method == 'POST':
        titre = periode.titre
        periode.delete()
        messages.success(request, f'Période "{titre}" supprimée.')
        return redirect('periodes:liste')
    return render(request, 'periodes/confirmer_suppression.html', {'periode': periode})


# ─── Changer le statut d'une période ────────────────────────────────────────
@admin_requis
def changer_statut(request, pk):
    periode = get_object_or_404(PeriodeVisite, pk=pk)
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in dict(PeriodeVisite.STATUTS):
            periode.statut = nouveau_statut
            periode.save()
            messages.success(request, f'Statut mis à jour : {periode.get_statut_display()}')
    return redirect('periodes:detail', pk=pk)


# ─── Import CSV étudiants ────────────────────────────────────────────────────
@admin_requis
def importer_csv(request, pk):
    periode = get_object_or_404(PeriodeVisite, pk=pk)
    form = ImportCSVForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        departement = form.cleaned_data['departement']
        etudiants   = form.get_etudiants()
        nb_importe  = 0
        nb_lie      = 0

        for etudiant in etudiants:
            if not etudiant['matricule']:
                continue

            obj, created = EtudiantImporte.objects.get_or_create(
                periode=periode,
                matricule=etudiant['matricule'],
                defaults={
                    'nom_complet': etudiant['nom_complet'],
                    'departement': departement,
                    'email':       etudiant['email'],
                }
            )

            # Lier automatiquement si le compte étudiant existe
            if created:
                nb_importe += 1
                try:
                    user = User.objects.get(matricule=etudiant['matricule'])
                    obj.user = user
                    obj.save()
                    nb_lie += 1
                except User.DoesNotExist:
                    pass

        messages.success(
            request,
            f'{nb_importe} étudiant(s) importé(s). '
            f'{nb_lie} compte(s) lié(s) automatiquement.'
        )
        return redirect('periodes:detail', pk=pk)

    return render(request, 'periodes/import_csv.html', {
        'form':    form,
        'periode': periode,
    })
