from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import ResultatMedical, RapportMedical
from .forms import ResultatMedicalForm, RapportMedicalForm
from rendezvous.models import RendezVous
from periodes.models import PeriodeVisite


def medecin_requis(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'medecin':
            messages.error(request, 'Accès réservé au personnel médical.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@medecin_requis
def rdv_du_jour(request):
    aujourd_hui = timezone.localdate()
    rdvs = RendezVous.objects.filter(
        creneau__date=aujourd_hui,
        creneau__periode__medecin=request.user,
    ).select_related('etudiant', 'creneau', 'creneau__periode').order_by('creneau__heure_debut')
    return render(request, 'resultats/rdv_du_jour.html', {
        'rdvs': rdvs,
        'aujourd_hui': aujourd_hui,
    })


@medecin_requis
def valider_presence(request, rdv_id):
    rdv = get_object_or_404(RendezVous, pk=rdv_id)
    if request.method == 'POST':
        statut = request.POST.get('statut')
        if statut in ['present', 'absent']:
            rdv.statut = statut
            rdv.save()
            messages.success(request, f'Présence mise à jour : {rdv.get_statut_display()}')
    return redirect('resultats:rdv_du_jour')


@medecin_requis
def saisir_resultat(request, rdv_id):
    rdv = get_object_or_404(RendezVous, pk=rdv_id)
    resultat = ResultatMedical.objects.filter(rendezvous=rdv).first()
    form = ResultatMedicalForm(request.POST or None, instance=resultat)

    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.rendezvous = rdv
        obj.etudiant   = rdv.etudiant
        obj.medecin    = request.user
        # calcul IMC automatique
        if obj.poids and obj.taille and obj.taille > 0:
            taille_m = obj.taille / 100
            obj.imc = round(obj.poids / (taille_m ** 2), 2)
        obj.save()
        messages.success(request, 'Résultats enregistrés avec succès.')
        return redirect('resultats:rdv_du_jour')

    return render(request, 'resultats/saisir_resultat.html', {
        'form': form,
        'rdv':  rdv,
    })


@medecin_requis
def rapport_general(request, periode_id):
    periode = get_object_or_404(PeriodeVisite, pk=periode_id)
    rapport = RapportMedical.objects.filter(periode=periode, medecin=request.user).first()
    form    = RapportMedicalForm(request.POST or None, instance=rapport)

    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.periode  = periode
        obj.medecin  = request.user
        # calcul automatique des stats
        rdvs = RendezVous.objects.filter(creneau__periode=periode)
        obj.nb_presents = rdvs.filter(statut='present').count()
        obj.nb_absents  = rdvs.filter(statut='absent').count()
        resultats = ResultatMedical.objects.filter(rendezvous__creneau__periode=periode)
        obj.nb_aptes   = resultats.filter(statut_aptitude='apte').count()
        obj.nb_inaptes = resultats.filter(statut_aptitude__in=['inapte', 'inapte_temporaire']).count()
        obj.save()
        messages.success(request, 'Rapport enregistré.')
        return redirect('resultats:rdv_du_jour')

    return render(request, 'resultats/rapport_general.html', {
        'form':    form,
        'periode': periode,
        'rapport': rapport,
    })


@login_required
def detail_resultat_etudiant(request, resultat_id):
    resultat = get_object_or_404(ResultatMedical, pk=resultat_id, etudiant=request.user)
    return render(request, 'resultats/detail_etudiant.html', {'resultat': resultat})