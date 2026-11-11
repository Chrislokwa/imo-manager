from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from .models import Contrat, Locataire, Paiement, Propriete


class DashboardViewTests(TestCase):
    def test_dashboard_displays_statistics(self):
        propriete = Propriete.objects.create(
            nom='Appartement test',
            adresse='1 rue de test',
            loyer_base=Decimal('8400.00'),
        )
        locataire = Locataire.objects.create(
            prenom='Jean',
            nom='Dupont',
            email='jean@example.com',
            telephone='0102030405',
        )
        contrat = Contrat.objects.create(
            propriete=propriete,
            locataire=locataire,
            date_debut=date(2026, 1, 1),
            date_fin=date(2027, 1, 1),
            loyer_mensuel=Decimal('8400.00'),
        )
        Paiement.objects.create(
            contrat=contrat,
            montant=Decimal('8400.00'),
            date_paiement=timezone.localdate().replace(day=1),
            statut='Payé',
            mois_concerne='Mois courant',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenue sur Imo !')
        self.assertContains(response, 'Total Biens')
        self.assertContains(response, '>1</p>')
        self.assertContains(response, 'Locataires Actifs')
        self.assertContains(response, '8400 €')
