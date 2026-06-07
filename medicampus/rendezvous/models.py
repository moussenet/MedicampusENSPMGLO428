from django.db import models
from accounts.models import User
from periodes.models import Creneau, PeriodeVisite


class RendezVous(models.Model):
    STATUTS = [
        ('confirme', 'Confirmé'),
        ('annule',   'Annulé'),
        ('present',  'Présent'),
        ('absent',   'Absent'),
    ]
    etudiant      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rendezvous')
    creneau       = models.ForeignKey(Creneau, on_delete=models.CASCADE, related_name='rendezvous_set')
    periode       = models.ForeignKey(PeriodeVisite, on_delete=models.CASCADE, related_name='rendezvous', null=True)
    statut        = models.CharField(max_length=20, choices=STATUTS, default='confirme')
    est_urgent    = models.BooleanField(default=False)
    rappel_envoye = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'rendezvous'
        unique_together = [('etudiant', 'creneau')]

    def __str__(self):
        return f"{self.etudiant} — {self.creneau}"

    @property
    def a_resultat(self):
        return hasattr(self, 'resultat')