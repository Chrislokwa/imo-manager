from django.db import migrations, models
import django.utils.timezone


def copy_existing_due_dates(apps, schema_editor):
    Paiement = apps.get_model('core', 'Paiement')
    for paiement in Paiement.objects.filter(date_echeance__isnull=True).iterator():
        paiement.date_echeance = paiement.date_paiement or django.utils.timezone.localdate()
        paiement.save(update_fields=['date_echeance'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='date_echeance',
            field=models.DateField(null=True, verbose_name="Date d'échéance"),
        ),
        migrations.AddField(
            model_name='paiement',
            name='rappel_envoye',
            field=models.BooleanField(default=False, verbose_name='Rappel envoyé'),
        ),
        migrations.AddField(
            model_name='paiement',
            name='date_rappel',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date du rappel'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='date_paiement',
            field=models.DateField(blank=True, null=True, verbose_name='Date du paiement'),
        ),
        migrations.RunPython(copy_existing_due_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='paiement',
            name='date_echeance',
            field=models.DateField(default=django.utils.timezone.localdate, verbose_name="Date d'échéance"),
        ),
    ]
