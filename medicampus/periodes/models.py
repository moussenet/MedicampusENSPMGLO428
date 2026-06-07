from django.db import models
from accounts.models import User

JOURS_OUVRABLES = [
    ('lundi',    'Lundi'),
    ('mardi',    'Mardi'),
    ('mercredi', 'Mercredi'),
    ('jeudi',    'Jeudi'),
    ('vendredi', 'Vendredi'),
]

DEPARTEMENTS = [
    ('GCA',     'Génie Civil et Architecture'),
    ('AGEPD',   'Agriculture, Élevage et Produits Dérivés'),
    ('INFOTEL', 'Informatique et Télécommunications'),
    ('HYMAE',   'Hydraulique et Maîtrise des Eaux'),
    ('SCIENV',  'Sciences Environnementales'),
    ('AHN',     'Art et Humanité Numérique'),
    ('ESB',     'Enseignement Scientifique de Base'),
    ('GTC',     'Génie Textile et Cuir'),
    ('ENREN',   'Énergies Renouvelables'),
    ('MCHP',    'Météorologie, Climatologie, Hydrologie, Pédologie'),
]


class PeriodeVisite(models.Model):
    STATUTS = [
        ('programmee', 'Programmée'),
        ('en_cours',   'En cours'),
        ('terminee',   'Terminée'),
        ('annulee',    'Annulée'),
    ]

    titre        = models.CharField(max_length=200)
    departement  = models.CharField(max_length=20, choices=DEPARTEMENTS)
    date_debut   = models.DateField()
    date_fin     = models.DateField()
    heure_debut  = models.TimeField(help_text="Heure de début des consultations")
    heure_fin    = models.TimeField(help_text="Heure de fin des consultations")
    capacite_par_creneau = models.PositiveIntegerField(default=4)
    statut       = models.CharField(max_length=20, choices=STATUTS, default='programmee')
    cree_par     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='periodes_creees')
    created_at   = models.DateTimeField(auto_now_add=True)
    notif_envoyee = models.BooleanField(default=False)
    medecin = models.ForeignKey(
    'accounts.User',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    limit_choices_to={'role': 'medecin', 'is_active': True},
    related_name='periodes_assignees',
    db_column='medecin_id',
    db_constraint=False   # gardé pour éviter qu'une nouvelle contrainte soit recréée
)

    class Meta:
        db_table  = 'periodes_visite'
        ordering  = ['-date_debut']
        verbose_name = 'Période de visite'

    def __str__(self):
        return f"{self.titre} — {self.departement} ({self.date_debut})"

    def generer_creneaux(self):
        """Génère automatiquement les créneaux de 1h pour chaque jour ouvrable."""
        from datetime import datetime, timedelta
        import math

        self.creneaux.all().delete()

        debut  = datetime.combine(self.date_debut, self.heure_debut)
        fin_j  = datetime.combine(self.date_debut, self.heure_fin)
        nb_par_jour = math.floor((fin_j - debut).seconds / 3600)

        current_date = self.date_debut
        while current_date <= self.date_fin:
            if current_date.weekday() < 5:  # lundi=0 … vendredi=4
                for i in range(nb_par_jour):
                    h_debut = datetime.combine(current_date, self.heure_debut)
                    h_debut += timedelta(hours=i)
                    h_fin   = h_debut + timedelta(hours=1)
                    Creneau.objects.create(
                        periode=self,
                        date=current_date,
                        heure_debut=h_debut.time(),
                        heure_fin=h_fin.time(),
                        capacite=self.capacite_par_creneau,
                    )
            current_date += timedelta(days=1)


class Creneau(models.Model):
    periode     = models.ForeignKey(PeriodeVisite, on_delete=models.CASCADE, related_name='creneaux')
    date        = models.DateField()
    heure_debut = models.TimeField()
    heure_fin   = models.TimeField()
    capacite    = models.PositiveIntegerField(default=4)

    class Meta:
        db_table = 'creneaux'
        ordering = ['date', 'heure_debut']

    @property
    def nb_inscrits(self):
        return self.rendezvous_set.filter(statut__in=['confirme', 'present']).count()

    @property
    def est_disponible(self):
        return self.nb_inscrits < self.capacite

    @property
    def places_restantes(self):
        return self.capacite - self.nb_inscrits

    def __str__(self):
        return f"{self.date} {self.heure_debut}–{self.heure_fin}"


class EtudiantImporte(models.Model):
    """Étudiants importés via CSV pour une période donnée."""
    periode      = models.ForeignKey(PeriodeVisite, on_delete=models.CASCADE, related_name='etudiants_importes')
    nom_complet  = models.CharField(max_length=200)
    matricule    = models.CharField(max_length=50)
    departement  = models.CharField(max_length=20, choices=DEPARTEMENTS)
    email        = models.EmailField(blank=True, null=True)
    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'etudiants_importes'

    def __str__(self):
        return f"{self.matricule} — {self.nom_complet}"