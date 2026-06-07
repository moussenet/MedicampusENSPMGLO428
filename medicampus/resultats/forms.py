from django import forms
from .models import ResultatMedical, RapportMedical


class ResultatMedicalForm(forms.ModelForm):
    class Meta:
        model  = ResultatMedical
        fields = [
            'tension_arterielle', 'poids', 'taille', 'glycemie',
            'tdr_paludisme', 'tdr_typhoide', 'tdr_vih',
            'tdr_autre', 'tdr_autre_resultat',
            'analyse_selles', 'analyse_selles_detail',
            'test_urinaire', 'test_urinaire_detail',
            'observations', 'recommandations', 'statut_aptitude',
        ]
        widgets = {
            'tension_arterielle':    forms.TextInput(attrs={'placeholder': 'ex: 120/80'}),
            'poids':                 forms.NumberInput(attrs={'step': '0.01'}),
            'taille':                forms.NumberInput(attrs={'step': '0.01'}),
            'glycemie':              forms.NumberInput(attrs={'step': '0.01'}),
            'analyse_selles_detail': forms.Textarea(attrs={'rows': 2}),
            'test_urinaire_detail':  forms.Textarea(attrs={'rows': 2}),
            'observations':          forms.Textarea(attrs={'rows': 3}),
            'recommandations':       forms.Textarea(attrs={'rows': 3}),
        }


class RapportMedicalForm(forms.ModelForm):
    class Meta:
        model  = RapportMedical
        fields = ['observations_generales']
        widgets = {
            'observations_generales': forms.Textarea(attrs={'rows': 5}),
        }