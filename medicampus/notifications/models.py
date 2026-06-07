from django.db import models
from accounts.models import User
from periodes.models import PeriodeVisite


class Notification(models.Model):
    TYPES = [
        ('visite_programmee',  'Visite programmée'),
        ('rappel_rdv',         'Rappel RDV'),
        ('resultat_disponible','Résultat disponible'),
        ('info',               'Information'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type        = models.CharField(max_length=30, choices=TYPES, default='info')
    titre       = models.CharField(max_length=150)
    message     = models.TextField()
    lu          = models.BooleanField(default=False)
    archivee    = models.BooleanField(default=False)
    rendezvous  = models.ForeignKey('rendezvous.RendezVous', on_delete=models.SET_NULL, null=True, blank=True)
    periode     = models.ForeignKey(PeriodeVisite, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} → {self.user}"