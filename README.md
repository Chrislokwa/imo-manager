# Imo Manager

Application web de gestion locative développée avec Django. Elle permet de suivre un portefeuille de biens, les locataires, les baux et les paiements.

## Fonctionnalités

- Tableau de bord avec indicateurs, revenus encaissés sur six mois et alertes de fin de bail.
- Gestion des biens immobiliers : liste, filtres par type, création, modification et fiche détaillée.
- Recherche des locataires par nom ou téléphone, création et fiche détaillée.
- Création de contrats de bail avec vérification des dates et des périodes qui se chevauchent.
- Enregistrement des paiements, statuts, reçus imprimables et suivi des retards.
- Préférences utilisateur pour le symbole de devise et le format d’affichage des dates. Le choix de devise change le symbole affiché ; il ne convertit pas les montants.
- Export des données Django au format JSON.

## Technologies

- Django 6.1 et Django ORM
- SQLite par défaut en développement ; PostgreSQL sélectionnable par configuration
- Templates Django, Tailwind CSS, HTMX et Alpine.js
- Chart.js pour le graphique des revenus
- Authentification intégrée de Django

Tailwind CSS, HTMX, Alpine.js et Chart.js sont chargés depuis des CDN ; une connexion Internet est donc nécessaire pour ces ressources dans l’interface.

## Installation locale sous Windows

Depuis le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvre ensuite [http://127.0.0.1:8000/](http://127.0.0.1:8000/) et connecte-toi avec le nom d’utilisateur et le mot de passe choisis lors de `createsuperuser`. L’administration Django est disponible sur [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

La base locale est `db.sqlite3`. L’application n’inclut pas de compte par défaut : crée le premier compte avec `createsuperuser`.

## Configuration

Les paramètres locaux se trouvent dans `.env`. Le fichier `.env.example` donne les variables reconnues ; `.env` et la base SQLite sont exclus de Git.

### SQLite

SQLite est sélectionné par défaut. Tu peux aussi écrire ceci dans `.env` :

```dotenv
DJANGO_DB_ENGINE=sqlite
```

### PostgreSQL

Pour utiliser PostgreSQL, installe et démarre le serveur, crée la base, puis renseigne dans `.env` :

```dotenv
DJANGO_DB_ENGINE=postgresql
DB_NAME=immobilisation
DB_USER=postgres
DB_PASSWORD=ton-mot-de-passe
DB_HOST=localhost
DB_PORT=5432
```

Le pilote PostgreSQL est fourni dans `requirements.txt`.

En production, définis également une clé secrète `DJANGO_SECRET_KEY`, désactive `DJANGO_DEBUG` et configure `DJANGO_ALLOWED_HOSTS` pour les domaines réellement utilisés.

## Commandes utiles

Vérifier la configuration Django :

```powershell
python manage.py check
```

Prévisualiser les rappels qui seraient traités, sans modifier la base ni envoyer d’e-mail :

```powershell
python manage.py process_rent_reminders --dry-run
```

Exporter les données Django en JSON dans un fichier horodaté :

```powershell
python manage.py export_data
```

Choisir un chemin de sauvegarde :

```powershell
python manage.py export_data --output C:\Sauvegardes\imo.json
```

Les sauvegardes peuvent contenir des données personnelles : garde-les dans un emplacement privé et ne les publie pas sur GitHub.

## Rappels planifiés

La commande `process_rent_reminders` marque les paiements échus comme en retard et envoie un rappel par e-mail pour chaque paiement impayé qui n’a pas encore été rappelé.

En développement, Django utilise le backend e-mail console : les messages sont écrits dans la sortie de la commande. Pour envoyer de vrais e-mails, configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` et `DEFAULT_FROM_EMAIL` dans `.env`.

Sous Windows, après configuration du serveur e-mail, programme la tâche quotidienne de 09:00 avec :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_rent_reminders_task.ps1
```

La tâche s’exécute sous ton compte Windows lorsqu’il est connecté. Les instructions pour Linux et cron sont dans [TACHES_PLANIFIEES.md](TACHES_PLANIFIEES.md).

## Structure principale

```text
config/       Configuration Django et routes du projet
core/         Modèles, formulaires, vues, commandes et migrations
templates/    Pages HTML et composants d’interface
scripts/      Scripts de planification Windows
static/       Fichiers statiques
manage.py     Outil de gestion Django
```
