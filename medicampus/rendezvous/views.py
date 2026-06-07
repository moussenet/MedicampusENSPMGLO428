from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RendezVous
from periodes.models import PeriodeVisite, Creneau
from notifications.models import Notification


def etudiant_requis(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'etudiant':
            messages.error(request, 'Accès réservé aux étudiants.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@etudiant_requis
def periodes_disponibles(request):
    periodes = PeriodeVisite.objects.filter(
        statut__in=['programmee', 'en_cours'],
        departement=request.user.departement,
    ).order_by('date_debut')

    # Pour chaque période, vérifier si l'étudiant a déjà un RDV
    periodes_data = []
    for p in periodes:
        rdv = RendezVous.objects.filter(
            etudiant=request.user,
            creneau__periode=p,
        ).first()
        periodes_data.append({'periode': p, 'rdv': rdv})

    return render(request, 'rendezvous/periodes_disponibles.html', {
        'periodes_data': periodes_data,
    })


@etudiant_requis
def prendre_rdv(request, creneau_id):
    creneau = get_object_or_404(Creneau, pk=creneau_id)

    # Vérifier que le créneau est disponible
    if not creneau.est_disponible:
        messages.error(request, 'Ce créneau est complet.')
        return redirect('rendezvous:periodes_disponibles')

    # Vérifier que l'étudiant n'a pas déjà un RDV pour cette période
    deja = RendezVous.objects.filter(
        etudiant=request.user,
        creneau__periode=creneau.periode,
    ).exists()
    if deja:
        messages.error(request, 'Vous avez déjà un rendez-vous pour cette période.')
        return redirect('rendezvous:periodes_disponibles')

    if request.method == 'POST':
        rdv = RendezVous.objects.create(
            etudiant=request.user,
            creneau=creneau,
            periode=creneau.periode,
            statut='confirme',
        )
        # Notification de confirmation
        Notification.objects.create(
            user=request.user,
            type='rappel_rdv',
            titre='Rendez-vous confirmé',
            message=f'Votre RDV est confirmé pour le {creneau.date} de {creneau.heure_debut} à {creneau.heure_fin}.',
            rendezvous=rdv,
            periode=creneau.periode,
        )
        messages.success(request, 'Rendez-vous pris avec succès.')
        return redirect('rendezvous:mes_rendezvous')

    return render(request, 'rendezvous/confirmer_rdv.html', {'creneau': creneau})


@etudiant_requis
def annuler_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, pk=rdv_id, etudiant=request.user)
    if request.method == 'POST':
        rdv.statut = 'annule'
        rdv.save()
        messages.success(request, 'Rendez-vous annulé.')
    return redirect('rendezvous:mes_rendezvous')


@etudiant_requis
def mes_rendezvous(request):
    rdvs = RendezVous.objects.filter(
        etudiant=request.user,
    ).select_related('creneau', 'creneau__periode').order_by('-creneau__date')
    return render(request, 'rendezvous/mes_rendezvous.html', {'rdvs': rdvs})
