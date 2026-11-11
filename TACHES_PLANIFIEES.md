# Rappels de loyer planifiés

La commande `python manage.py process_rent_reminders` met à jour les paiements échus et envoie un seul e-mail de rappel pour chaque paiement impayé. Les paiements déjà marqués comme réglés ou rappelés sont ignorés.

En développement, l’application utilise le backend e-mail console de Django : les messages apparaissent dans la sortie de la commande. Pour envoyer de vrais e-mails, renseignez `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` et `DEFAULT_FROM_EMAIL` dans `.env`. Le script Windows refuse de créer la tâche tant que `EMAIL_HOST` n'est pas configuré.

Pour prévisualiser le nombre de paiements concernés sans envoyer d’e-mail ni modifier la base :

```powershell
python manage.py process_rent_reminders --dry-run
```

Sous Windows, depuis le dossier du projet, enregistrez la tâche quotidienne de 09:00 avec :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_rent_reminders_task.ps1
```

La tâche s’exécute sous le compte Windows courant lorsque celui-ci est connecté. Sous Linux, ajoutez une entrée cron quotidienne, en adaptant le chemin Python et le dossier du projet :

```cron
0 9 * * * cd /chemin/vers/Imo && /chemin/vers/python manage.py process_rent_reminders
```
