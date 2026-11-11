import io
import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Exporte les données Django dans un fichier JSON de sauvegarde.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            help='Chemin du fichier JSON de destination. Par défaut, un fichier horodaté est créé ici.',
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=2,
            help='Nombre d’espaces d’indentation du JSON (défaut : 2).',
        )

    def handle(self, *args, **options):
        if options['indent'] < 0:
            raise CommandError('--indent doit être supérieur ou égal à zéro.')

        if options['output']:
            destination = Path(options['output']).expanduser()
            if destination.suffix.lower() != '.json':
                destination = destination.with_suffix('.json')
        else:
            horodatage = timezone.localtime().strftime('%Y%m%d_%H%M%S')
            destination = Path.cwd() / f'imo_backup_{horodatage}.json'

        if destination.exists():
            raise CommandError(f'Le fichier existe déjà : {destination}')

        contenu = io.StringIO()
        call_command('dumpdata', exclude=['sessions'], indent=options['indent'], stdout=contenu)
        try:
            donnees = json.loads(contenu.getvalue())
        except json.JSONDecodeError as erreur:
            raise CommandError(f'La sauvegarde générée n’est pas un JSON valide : {erreur}') from erreur

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(donnees, ensure_ascii=False, indent=options['indent']) + '\n', encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'Sauvegarde exportée : {destination.resolve()}'))
