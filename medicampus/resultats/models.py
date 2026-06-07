from django.db import models
from accounts.models import User
from rendezvous.models import RendezVous
from periodes.models import PeriodeVisite


class ResultatMedical(models.Model):
    TDR = [
        ('positif',  'Positif'),
        ('negatif',  'Négatif'),
        ('non_fait', 'Non fait'),
    ]
    ANALYSE = [
        ('normal',   'Normal'),
        ('anormal',  'Anormal'),
        ('non_fait', 'Non fait'),
    ]
    APTITUDE = [
        ('apte',                'Apte'),
        ('apte_avec_reserves',  'Apte avec réserves'),
        ('inapte_temporaire',   'Inapte temporaire'),
        ('inapte',              'Inapte'),
    ]

    rendezvous             = models.OneToOneField(RendezVous, on_delete=models.CASCADE, related_name='resultat')
    etudiant               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultats')
    medecin                = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultats_saisis')
    tension_arterielle     = models.CharField(max_length=20, blank=True, null=True)
    poids                  = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    taille                 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    imc                    = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    glycemie               = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tdr_paludisme          = models.CharField(max_length=10, choices=TDR, default='non_fait')
    tdr_typhoide           = models.CharField(max_length=10, choices=TDR, default='non_fait')
    tdr_vih                = models.CharField(max_length=10, choices=TDR, default='non_fait')
    tdr_autre              = models.CharField(max_length=100, blank=True, null=True)
    tdr_autre_resultat     = models.CharField(max_length=10, choices=TDR, default='non_fait')
    analyse_selles         = models.CharField(max_length=10, choices=ANALYSE, default='non_fait')
    analyse_selles_detail  = models.TextField(blank=True, null=True)
    test_urinaire          = models.CharField(max_length=10, choices=ANALYSE, default='non_fait')
    test_urinaire_detail   = models.TextField(blank=True, null=True)
    observations           = models.TextField(blank=True, null=True)
    recommandations        = models.TextField(blank=True, null=True)
    statut_aptitude        = models.CharField(max_length=25, choices=APTITUDE, default='apte')
    created_at             = models.DateTimeField(auto_now_add=True)
    updated_at             = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resultats_medicaux'

    def __str__(self):
        return f"Résultat de {self.etudiant} — {self.created_at.date()}"


class RapportMedical(models.Model):
    periode                 = models.ForeignKey(PeriodeVisite, on_delete=models.CASCADE, related_name='rapports')
    medecin                 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports')
    nb_presents             = models.IntegerField(default=0)
    nb_absents              = models.IntegerField(default=0)
    nb_aptes                = models.IntegerField(default=0)
    nb_inaptes              = models.IntegerField(default=0)
    observations_generales  = models.TextField(blank=True, null=True)
    lu_admin                = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rapports_medicaux'

    def __str__(self):
        return f"Rapport {self.periode} — {self.medecin}"