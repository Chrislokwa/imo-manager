from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Propriete(models.Model):
    TYPES_BIENS = [
        ('Appartement', 'Appartement'),
        ('Maison', 'Maison'),
        ('Commercial', 'Commercial'),
        ('Villa', 'Villa'),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom / Référence")
    adresse = models.TextField(verbose_name="Adresse complète")
    type_bien = models.CharField(max_length=50, choices=TYPES_BIENS, default='Appartement')
    loyer_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Loyer mensuel de base")
    est_occupe = models.BooleanField(default=False, verbose_name="Est occupé ?")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.type_bien})"


class Locataire(models.Model):
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    contact_urgence = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact d'urgence")
    date_arrivee = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Contrat(models.Model):
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, verbose_name="Bien immobilier")
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE, verbose_name="Locataire")
    date_debut = models.DateField(verbose_name="Date de début du bail")
    date_fin = models.DateField(verbose_name="Date de fin du bail")
    loyer_mensuel = models.DecimalField(max_digits=10, decimal_places=2)
    actif = models.BooleanField(default=True, verbose_name="Contrat actif")

    def clean(self):
        super().clean()
        erreurs = {}
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            erreurs['date_fin'] = "La date de fin doit être postérieure à la date de début."

        if self.propriete_id and self.date_debut and self.date_fin and self.actif:
            chevauchement = Contrat.objects.filter(
                propriete_id=self.propriete_id,
                actif=True,
                date_debut__lte=self.date_fin,
                date_fin__gte=self.date_debut,
            )
            if self.pk:
                chevauchement = chevauchement.exclude(pk=self.pk)
            if chevauchement.exists():
                erreurs['propriete'] = "Ce bien a déjà un contrat actif sur cette période."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        self.full_clean()
        resultat = super().save(*args, **kwargs)
        self._actualiser_statut_bien()
        return resultat

    def delete(self, *args, **kwargs):
        propriete_id = self.propriete_id
        resultat = super().delete(*args, **kwargs)
        self._actualiser_statut_bien(propriete_id)
        return resultat

    @staticmethod
    def _actualiser_statut_bien(propriete_id):
        if not propriete_id:
            return
        aujourd_hui = timezone.localdate()
        occupe = Contrat.objects.filter(
            propriete_id=propriete_id,
            actif=True,
            date_debut__lte=aujourd_hui,
            date_fin__gte=aujourd_hui,
        ).exists()
        Propriete.objects.filter(pk=propriete_id).update(est_occupe=occupe)

    def __str__(self):
        return f"Bail : {self.locataire} -> {self.propriete.nom}"


class Paiement(models.Model):
    STATUTS_PAIEMENT = [
        ('Payé', 'Payé'),
        ('En attente', 'En attente'),
        ('En retard', 'En retard'),
    ]
    METHODES_PAIEMENT = [
        ('Espèces', 'Espèces'),
        ('Virement', 'Virement'),
        ('Chèque', 'Chèque'),
        ('En ligne', 'En ligne'),
    ]

    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE, verbose_name="Contrat associé")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_echeance = models.DateField(default=timezone.localdate, verbose_name="Date d'échéance")
    date_paiement = models.DateField(blank=True, null=True, verbose_name="Date du paiement")
    statut = models.CharField(max_length=20, choices=STATUTS_PAIEMENT, default='En attente')
    methode = models.CharField(max_length=20, choices=METHODES_PAIEMENT, default='Virement')
    mois_concerne = models.CharField(max_length=20, verbose_name="Mois concerné (ex: Janvier 2026)")
    rappel_envoye = models.BooleanField(default=False, verbose_name="Rappel envoyé")
    date_rappel = models.DateTimeField(blank=True, null=True, verbose_name="Date du rappel")

    def __str__(self):
        return f"Paiement {self.montant}€ - {self.statut} ({self.mois_concerne})"


class UserPreference(models.Model):
    DEVISES = [
        ('EUR', 'Euro (€)'),
        ('USD', 'Dollar américain ($)'),
        ('GBP', 'Livre sterling (£)'),
        ('MAD', 'Dirham marocain (د.م.)'),
    ]
    FORMATS_DATE = [
        ('DMY', 'Jour / mois / année (31/12/2026)'),
        ('MDY', 'Mois / jour / année (12/31/2026)'),
        ('ISO', 'Année-mois-jour (2026-12-31)'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    devise = models.CharField(max_length=3, choices=DEVISES, default='EUR')
    format_date = models.CharField(max_length=3, choices=FORMATS_DATE, default='DMY')

    def __str__(self):
        return f'Préférences de {self.user.get_username()}'
