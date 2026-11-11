from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Paiement


class Command(BaseCommand):
    help = 'Marque les loyers échus en retard et envoie les rappels de paiement manquants.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les actions prévues sans modifier les paiements ni envoyer de messages.',
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        paiements_a_traiter = Paiement.objects.filter(date_echeance__lt=today).exclude(statut='Payé')
        nombres_a_marquer = paiements_a_traiter.exclude(statut='En retard').count()
        rappels = list(
            paiements_a_traiter.filter(statut='En retard', rappel_envoye=False)
            .select_related('contrat__locataire', 'contrat__propriete')
        )

        if options['dry_run']:
            self.stdout.write(
                f'{nombres_a_marquer} paiement(s) à marquer en retard ; '
                f'{len(rappels)} rappel(s) à envoyer.'
            )
            return

        paiements_a_traiter.exclude(statut='En retard').update(statut='En retard')
        rappels_envoyes = 0
        for paiement in rappels:
            locataire = paiement.contrat.locataire
            bien = paiement.contrat.propriete
            sujet = f"Rappel de loyer : {paiement.mois_concerne}"
            message = (
                f"Bonjour {locataire.prenom},\n\n"
                f"Nous vous rappelons que le paiement du loyer de {paiement.mois_concerne} "
                f"pour le bien {bien.nom} ( {bien.adresse} ) est arrivé à échéance le "
                f"{paiement.date_echeance:%d/%m/%Y}.\n"
                f"Montant dû : {paiement.montant:.2f} €.\n\n"
                "Si vous avez déjà réglé ce loyer, veuillez ignorer ce message.\n"
                "Cordialement,\nImo Manager"
            )
            nombre_envoye = send_mail(
                sujet,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [locataire.email],
                fail_silently=False,
            )
            if nombre_envoye:
                paiement.rappel_envoye = True
                paiement.date_rappel = timezone.now()
                paiement.save(update_fields=['rappel_envoye', 'date_rappel'])
                rappels_envoyes += 1

        self.stdout.write(self.style.SUCCESS(
            f'{nombres_a_marquer} paiement(s) marqué(s) en retard ; '
            f'{rappels_envoyes} rappel(s) envoyé(s).'
        ))
