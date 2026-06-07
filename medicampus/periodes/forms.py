from django import forms
from .models import PeriodeVisite, DEPARTEMENTS
from accounts.models import User
import csv
import io


class PeriodeVisiteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medecin'].queryset = User.objects.filter(
            role='medecin', is_active=True
        ).order_by('last_name')
        self.fields['medecin'].empty_label = '-- Choisir un personnel medical --'

    class Meta:
        model  = PeriodeVisite
        fields = [
            'titre', 'departement', 'medecin', 'date_debut', 'date_fin',
            'heure_debut', 'heure_fin', 'capacite_par_creneau'
        ]
        labels = {
            'titre':                'Titre de la visite',
            'departement':          'Departement concerne',
            'medecin':              'Personnel medical assigne',
            'date_debut':           'Date de debut',
            'date_fin':             'Date de fin',
            'heure_debut':          'Heure de debut',
            'heure_fin':            'Heure de fin',
            'capacite_par_creneau': 'Capacite par creneau',
        }
        widgets = {
            'titre':                forms.TextInput(attrs={'placeholder': 'Ex: Visite medicale annuelle 2025'}),
            'date_debut':           forms.DateInput(attrs={'type': 'date'}),
            'date_fin':             forms.DateInput(attrs={'type': 'date'}),
            'heure_debut':          forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin':            forms.TimeInput(attrs={'type': 'time'}),
            'capacite_par_creneau': forms.NumberInput(attrs={'min': 1, 'max': 20}),
        }

    def clean(self):
        cleaned     = super().clean()
        date_debut  = cleaned.get('date_debut')
        date_fin    = cleaned.get('date_fin')
        heure_debut = cleaned.get('heure_debut')
        heure_fin   = cleaned.get('heure_fin')

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error('date_fin', 'La date de fin doit etre apres la date de debut.')

        if heure_debut and heure_fin and heure_fin <= heure_debut:
            self.add_error('heure_fin', "L'heure de fin doit etre apres l'heure de debut.")

        return cleaned


class ImportCSVForm(forms.Form):
    departement = forms.ChoiceField(
        choices=[('', '-- Choisir un departement --')] + list(DEPARTEMENTS),
        label='Departement'
    )
    fichier_csv = forms.FileField(
        label='Fichier CSV des etudiants',
        help_text='Format attendu : matricule, nom_complet, email'
    )

    def clean_fichier_csv(self):
        fichier = self.cleaned_data.get('fichier_csv')

        if not fichier.name.endswith('.csv'):
            raise forms.ValidationError('Le fichier doit etre au format .csv')

        if fichier.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Le fichier ne doit pas depasser 5 Mo.')

        try:
            content = fichier.read().decode('utf-8-sig')
            fichier.seek(0)
            reader  = csv.DictReader(io.StringIO(content))
            colonnes = reader.fieldnames or []
            colonnes = [c.strip().lower() for c in colonnes]

            if 'matricule' not in colonnes or 'nom_complet' not in colonnes:
                raise forms.ValidationError(
                    'Colonnes requises manquantes. Le fichier doit contenir : '
                    'matricule, nom_complet (et optionnellement email).'
                )
        except UnicodeDecodeError:
            raise forms.ValidationError('Encodage non supporte. Sauvegardez le CSV en UTF-8.')

        return fichier

    def get_etudiants(self):
        fichier = self.cleaned_data['fichier_csv']
        fichier.seek(0)
        content = fichier.read().decode('utf-8-sig')
        reader  = csv.DictReader(io.StringIO(content))
        etudiants = []
        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            etudiants.append({
                'matricule':   row.get('matricule', ''),
                'nom_complet': row.get('nom_complet', ''),
                'email':       row.get('email', ''),
            })
        return etudiants