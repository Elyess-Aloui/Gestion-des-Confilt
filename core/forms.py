from django import forms
from .models import GOUVERNORATS, NIVEAUX, SALLE_TYPES

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )

class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

class InstitutForm(forms.Form):
    nom = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Institut Supérieur des Études'})
    )
    region = forms.ChoiceField(
        choices=GOUVERNORATS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ville = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Tunis, La Marsa'})
    )

class SalleForm(forms.Form):
    numero = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salle 101, Labo A'})
    )
    type = forms.ChoiceField(
        choices=SALLE_TYPES,
        initial='normale',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    capacite = forms.IntegerField(
        min_value=1,
        initial=30,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 30'})
    )

class SalleBreakdownForm(forms.Form):
    broken_duration = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 48 heures, 3 jours'})
    )

class MatiereForm(forms.Form):
    nom = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mathématiques, Français, Histoire'})
    )
    niveaux = forms.MultipleChoiceField(
        choices=NIVEAUX,
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    volume_horaire = forms.IntegerField(
        min_value=1,
        max_value=60,
        initial=4,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 4 (heures/semaine)'})
    )

class EnseignantForm(forms.Form):
    nom = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet (ex: Dr. Ben Salem)'})
    )
    niveaux = forms.CharField(
        max_length=200,
        initial='Niveau 1, Niveau 2',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Niveau 1, Niveau 2, Niveau 3'})
    )
    volume_horaire = forms.IntegerField(
        min_value=1,
        max_value=60,
        initial=18,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 18 (heures max/semaine)'})
    )

class AbsenceClaimForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motif de l\'absence'})
    )
    date_start = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_end = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class ClasseForm(forms.Form):
    niveau = forms.ChoiceField(
        choices=NIVEAUX,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nom = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A, B, C'})
    )
