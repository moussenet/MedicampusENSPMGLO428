from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    ROLES = [
        ('superadmin', 'Super Administrateur'),
        ('admin',      'Administrateur'),
        ('medecin',    'Personnel médical'),
        ('etudiant',   'Étudiant'),
    ]

    role        = models.CharField(max_length=20, choices=ROLES, default='etudiant')
    matricule   = models.CharField(max_length=30, blank=True, null=True, unique=True)
    departement = models.CharField(max_length=150, blank=True, null=True)
    filiere     = models.CharField(max_length=150, blank=True, null=True)

    # Médecin
    specialite = models.CharField(max_length=100, blank=True, null=True)

    # Administrateur — code ENSPM saisi à la création
    id_direction = models.CharField(max_length=50, blank=True, null=True)

    # Contact WhatsApp (notifications)
    whatsapp         = models.CharField(max_length=20, blank=True, null=True)
    callmebot_apikey = models.CharField(max_length=50, blank=True, null=True)

    # Email unique obligatoire — sert de login
    email = models.EmailField(unique=True, verbose_name='Adresse email')

    # Login par email au lieu de username
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.role})"

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_medecin(self):
        return self.role == 'medecin'

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'

    def get_display_name(self):
        full = self.get_full_name().strip()
        return full if full else self.email


class CodeValidationENSPM(models.Model):
    """
    Codes générés par la direction ENSPM pour valider
    la création d'un compte Administrateur.
    """
    code        = models.CharField(max_length=50, unique=True)
    est_utilise = models.BooleanField(default=False)
    utilise_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='code_utilise'
    )
    cree_par   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='codes_crees'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'codes_validation_enspm'
        verbose_name = 'Code de validation ENSPM'

    def __str__(self):
        status = 'utilisé' if self.est_utilise else 'disponible'
        return f"{self.code} — {status}"