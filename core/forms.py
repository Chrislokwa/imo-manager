from django import forms
from django.utils import timezone

from .models import Contrat, Locataire, Paiement, Propriete, UserPreference


FORM_CONTROL_CLASS = 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200'


class ProprieteForm(forms.ModelForm):
    class Meta:
        model = Propriete
        fields = ['nom', 'adresse', 'type_bien', 'loyer_base']
        widgets = {
            'nom': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'adresse': forms.Textarea(attrs={'class': FORM_CONTROL_CLASS, 'rows': 3}),
            'type_bien': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'loyer_base': forms.NumberInput(attrs={'class': FORM_CONTROL_CLASS, 'min': '0.01', 'step': '0.01'}),
        }


class LocataireForm(forms.ModelForm):
    class Meta:
        model = Locataire
        fields = ['prenom', 'nom', 'email', 'telephone', 'contact_urgence']
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'email': 'Adresse e-mail',
            'telephone': 'Téléphone',
            'contact_urgence': "Contact d'urgence",
        }
        widgets = {
            'prenom': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS, 'autocomplete': 'given-name'}),
            'nom': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS, 'autocomplete': 'family-name'}),
            'email': forms.EmailInput(attrs={'class': FORM_CONTROL_CLASS, 'autocomplete': 'email'}),
            'telephone': forms.TelInput(attrs={'class': FORM_CONTROL_CLASS, 'autocomplete': 'tel'}),
            'contact_urgence': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS, 'placeholder': 'Nom et téléphone (facultatif)'}),
        }


class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['propriete', 'locataire', 'loyer_mensuel', 'date_debut', 'date_fin']
        labels = {
            'propriete': 'Bien immobilier',
            'locataire': 'Locataire',
            'loyer_mensuel': 'Montant du loyer mensuel',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
        }
        widgets = {
            'propriete': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'locataire': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'loyer_mensuel': forms.NumberInput(attrs={'class': FORM_CONTROL_CLASS, 'min': '0.01', 'step': '0.01'}),
            'date_debut': forms.DateInput(attrs={'class': FORM_CONTROL_CLASS, 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': FORM_CONTROL_CLASS, 'type': 'date'}),
        }

    def __init__(self, *args, propriete=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriete is not None:
            self.fields['propriete'].initial = propriete
            self.fields['propriete'].queryset = Propriete.objects.filter(pk=propriete.pk)


class PaiementForm(forms.ModelForm):
    montant = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': FORM_CONTROL_CLASS, 'min': '0.01', 'step': '0.01'}),
    )

    class Meta:
        model = Paiement
        fields = ['contrat', 'montant', 'date_echeance', 'date_paiement', 'methode', 'statut', 'mois_concerne']
        labels = {
            'contrat': 'Contrat et locataire',
            'montant': 'Montant réglé',
            'date_echeance': "Date d'échéance",
            'date_paiement': 'Date du règlement (si payé)',
            'methode': 'Mode de paiement',
            'statut': 'Statut du paiement',
            'mois_concerne': 'Mois concerné',
        }
        widgets = {
            'contrat': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'date_echeance': forms.DateInput(attrs={'class': FORM_CONTROL_CLASS, 'type': 'date'}),
            'date_paiement': forms.DateInput(attrs={'class': FORM_CONTROL_CLASS, 'type': 'date'}),
            'methode': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'statut': forms.Select(attrs={'class': FORM_CONTROL_CLASS, 'x-model': 'statut'}),
            'mois_concerne': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS, 'placeholder': 'ex. Novembre 2026'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        mois = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')
        self.fields['mois_concerne'].initial = f'{mois[today.month - 1].capitalize()} {today.year}'
        self.fields['date_echeance'].initial = today
        self.fields['date_paiement'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('statut') == 'Payé' and not cleaned_data.get('date_paiement'):
            self.add_error('date_paiement', 'Indiquez la date du règlement pour un paiement marqué Payé.')
        return cleaned_data


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['devise', 'format_date']
        labels = {
            'devise': 'Devise',
            'format_date': 'Format de date',
        }
        widgets = {
            'devise': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'format_date': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
        }
