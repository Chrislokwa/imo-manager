from django.contrib import admin
from .models import Propriete, Locataire, Contrat, Paiement, UserPreference

# Register your models here.
admin.site.register([Propriete, Locataire, Contrat, Paiement, UserPreference])
