from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, CodeValidationENSPM


# ─── Formulaire inscription étudiant ────────────────────────────────────────
class EtudiantRegisterForm(forms.ModelForm):
    prenom           = forms.CharField(required=False, label='Prénom')
    password         = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmer le mot de passe')

    class Meta:
        model  = User
        fields = ['last_name', 'prenom', 'email', 'matricule', 'departement', 'filiere']
        labels = {
            'last_name':  'Nom',
            'email':      'Adresse email',
            'matricule':  'Matricule',
            'departement':'Département',
            'filiere':    'Filière',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean_matricule(self):
        matricule = self.cleaned_data.get('matricule')
        if User.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError('Ce matricule est déjà enregistré.')
        return matricule

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Les mots de passe ne correspondent pas.')
        return cleaned

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.first_name = self.cleaned_data.get('prenom', '')
        user.role       = 'etudiant'
        user.username   = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.is_active  = True
        if commit:
            user.save()
        return user


# ─── Formulaire login ────────────────────────────────────────────────────────
class LoginForm(forms.Form):
    email    = forms.EmailField(label='Adresse email')
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')


# ─── Formulaire création compte admin/médecin par super-admin ───────────────
class CreateStaffForm(forms.ModelForm):
    prenom           = forms.CharField(required=False, label='Prénom')
    password         = forms.CharField(widget=forms.PasswordInput, label='Mot de passe temporaire')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmer')
    role             = forms.ChoiceField(
        choices=[('admin', 'Administrateur'), ('medecin', 'Personnel médical')],
        label='Rôle'
    )
    # Champ affiché uniquement pour les admins (validé côté view)
    code_enspm = forms.CharField(
        required=False,
        label='Code de validation ENSPM',
        help_text='Obligatoire pour le rôle Administrateur'
    )

    class Meta:
        model  = User
        fields = ['last_name', 'prenom', 'email', 'specialite']
        labels = {
            'last_name': 'Nom',
            'email':     'Adresse email',
            'specialite':'Spécialité (médecin)',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1   = cleaned.get('password')
        p2   = cleaned.get('confirm_password')
        role = cleaned.get('role')
        code = cleaned.get('code_enspm', '').strip()

        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Les mots de passe ne correspondent pas.')

        if role == 'admin':
            if not code:
                self.add_error('code_enspm', 'Le code ENSPM est obligatoire pour un administrateur.')
            else:
                try:
                    c = CodeValidationENSPM.objects.get(code=code, est_utilise=False)
                    cleaned['code_obj'] = c
                except CodeValidationENSPM.DoesNotExist:
                    self.add_error('code_enspm', 'Code invalide ou déjà utilisé.')

        return cleaned

    def save(self, created_by, commit=True):
        user            = super().save(commit=False)
        user.first_name = self.cleaned_data.get('prenom', '')
        user.role       = self.cleaned_data['role']
        user.username   = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.is_active  = True
        if commit:
            user.save()
            # Marquer le code comme utilisé si admin
            code_obj = self.cleaned_data.get('code_obj')
            if code_obj:
                code_obj.est_utilise = True
                code_obj.utilise_par = user
                code_obj.save()
        return user


# ─── Formulaire changement de mot de passe ──────────────────────────────────
class ChangePasswordForm(forms.Form):
    ancien_password  = forms.CharField(widget=forms.PasswordInput, label='Ancien mot de passe')
    nouveau_password = forms.CharField(widget=forms.PasswordInput, label='Nouveau mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmer')

    def clean_nouveau_password(self):
        password = self.cleaned_data.get('nouveau_password')
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('nouveau_password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Les mots de passe ne correspondent pas.')
        return cleaned