from datetime import date, timedelta

from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ContratForm, LocataireForm, PaiementForm, ProprieteForm, UserPreferenceForm
from .models import Contrat, Locataire, Paiement, Propriete, UserPreference


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    revenus_total = Paiement.objects.filter(
        statut='Payé',
        date_paiement__year=today.year,
        date_paiement__month=today.month,
    ).aggregate(total=Sum('montant'))['total'] or 0

    mois_fr = ('Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre')
    six_mois = []
    for decalage in range(5, -1, -1):
        index_mois = today.year * 12 + today.month - 1 - decalage
        annee, mois_index = divmod(index_mois, 12)
        six_mois.append((annee, mois_index + 1))

    debut_periode = date(six_mois[0][0], six_mois[0][1], 1)
    revenus_par_mois = {
        (ligne['mois'].year, ligne['mois'].month): ligne['total']
        for ligne in Paiement.objects.filter(
            statut='Payé',
            date_paiement__gte=debut_periode,
            date_paiement__lte=today,
        ).annotate(mois=TruncMonth('date_paiement'))
        .values('mois')
        .annotate(total=Sum('montant'))
    }
    graphique_labels = [f'{mois_fr[mois - 1]} {annee}' for annee, mois in six_mois]
    graphique_revenus = [float(revenus_par_mois.get((annee, mois), 0)) for annee, mois in six_mois]

    limite_expiration = today + timedelta(days=30)
    contrats_a_renouveler = list(
        Contrat.objects.filter(
            actif=True,
            date_debut__lte=today,
            date_fin__gte=today,
            date_fin__lte=limite_expiration,
        ).select_related('locataire', 'propriete').order_by('date_fin')
    )
    for contrat in contrats_a_renouveler:
        contrat.jours_avant_expiration = (contrat.date_fin - today).days

    return render(request, 'core/dashboard.html', {
        'total_biens': Propriete.objects.count(),
        'total_locataires': Contrat.objects.filter(actif=True)
        .values('locataire_id')
        .distinct()
        .count(),
        'total_contrats_actifs': Contrat.objects.filter(
            actif=True, date_debut__lte=today, date_fin__gte=today,
        ).count(),
        'paiements_en_retard': Paiement.objects.filter(
            date_echeance__lt=today,
        ).exclude(statut='Payé').count(),
        'revenus_total': revenus_total,
        'graphique_labels': graphique_labels,
        'graphique_revenus': graphique_revenus,
        'contrats_a_renouveler': contrats_a_renouveler,
    })


@login_required
def biens_list_view(request):
    """Affiche les biens et permet de les filtrer sans recharger la page."""
    biens = Propriete.objects.all().order_by('-date_creation')
    type_bien = request.GET.get('type', '')
    if type_bien:
        biens = biens.filter(type_bien=type_bien)
    context = {
        'biens': biens,
        'types_biens': Propriete.TYPES_BIENS,
        'type_selectionne': type_bien,
    }
    template = 'core/_biens_rows.html' if request.headers.get('HX-Request') == 'true' else 'core/biens_list.html'
    return render(request, template, context)


@login_required
def bien_detail_view(request, pk):
    bien = get_object_or_404(Propriete, pk=pk)
    today = timezone.localdate()
    contrats = bien.contrat_set.select_related('locataire').order_by('-date_debut')
    contrats_en_cours = contrats.filter(actif=True, date_debut__lte=today, date_fin__gte=today)
    contrats_a_venir = contrats.filter(actif=True, date_debut__gt=today)
    contrats_expires = contrats.filter(Q(date_fin__lt=today) | Q(actif=False))
    bien.est_occupe = contrats_en_cours.exists()
    return render(request, 'core/bien_detail.html', {
        'bien': bien,
        'contrats_en_cours': contrats_en_cours,
        'contrats_a_venir': contrats_a_venir,
        'contrats_expires': contrats_expires,
    })


@login_required
def contrat_create_view(request, propriete_pk=None):
    propriete = get_object_or_404(Propriete, pk=propriete_pk) if propriete_pk else None
    if request.method == 'POST':
        form = ContratForm(request.POST, propriete=propriete)
        if form.is_valid():
            contrat = form.save()
            return redirect('bien_detail', pk=contrat.propriete_id)
    else:
        form = ContratForm(propriete=propriete)
    return render(request, 'core/contrat_form.html', {'form': form, 'propriete': propriete})

@login_required
def bien_create_view(request):
    """Ajoute un nouveau bien"""
    if request.method == 'POST':
        form = ProprieteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('biens_list')
    else:
        form = ProprieteForm()
    return render(request, 'core/bien_form.html', {'form': form, 'action': 'Ajouter'})

@login_required
def bien_update_view(request, pk):
    """Modifie un bien existant"""
    bien = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        form = ProprieteForm(request.POST, instance=bien)
        if form.is_valid():
            form.save()
            return redirect('biens_list')
    else:
        form = ProprieteForm(instance=bien)
    return render(request, 'core/bien_form.html', {'form': form, 'action': 'Modifier'})

@login_required
def bien_delete_view(request, pk):
    """Supprime un bien"""
    bien = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        bien.delete()
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'core/_bien_deleted.html')
        return redirect('biens_list')
    return render(request, 'core/bien_confirm_delete.html', {'bien': bien})


@login_required
def locataires_list_view(request):
    recherche = request.GET.get('q', '').strip()
    locataires = Locataire.objects.all().order_by('nom', 'prenom')
    if recherche:
        locataires = locataires.filter(
            Q(prenom__icontains=recherche)
            | Q(nom__icontains=recherche)
            | Q(telephone__icontains=recherche)
        )
    contrats = Contrat.objects.filter(
        locataire_id__in=locataires.values('pk'),
        actif=True,
        date_debut__lte=timezone.localdate(),
        date_fin__gte=timezone.localdate(),
    ).select_related('propriete', 'locataire')
    contrat_par_locataire = {contrat.locataire_id: contrat for contrat in contrats}
    for locataire in locataires:
        locataire.contrat_en_cours = contrat_par_locataire.get(locataire.pk)
    context = {
        'locataires': locataires,
        'recherche': recherche,
    }
    template = 'core/_locataires_rows.html' if request.headers.get('HX-Request') == 'true' else 'core/locataires_list.html'
    return render(request, template, context)


@login_required
def locataire_create_view(request):
    if request.method == 'POST':
        form = LocataireForm(request.POST)
        if form.is_valid():
            locataire = form.save()
            return redirect('locataire_detail', pk=locataire.pk)
    else:
        form = LocataireForm()
    return render(request, 'core/locataire_form.html', {'form': form})


@login_required
def locataire_detail_view(request, pk):
    locataire = get_object_or_404(Locataire, pk=pk)
    today = timezone.localdate()
    contrats = locataire.contrat_set.select_related('propriete').order_by('-date_debut')
    contrat_en_cours = contrats.filter(
        actif=True, date_debut__lte=today, date_fin__gte=today,
    ).first()
    return render(request, 'core/locataire_detail.html', {
        'locataire': locataire,
        'contrats': contrats,
        'contrat_en_cours': contrat_en_cours,
    })


@login_required
def paiements_list_view(request):
    _marquer_paiements_en_retard()
    paiements = Paiement.objects.select_related(
        'contrat__locataire', 'contrat__propriete',
    ).order_by('-date_paiement', '-pk')
    return render(request, 'paiements/liste_paiements.html', {'paiements': paiements})


def _marquer_paiements_en_retard():
    today = timezone.localdate()
    Paiement.objects.filter(date_echeance__lt=today).exclude(
        statut='Payé',
    ).exclude(statut='En retard').update(statut='En retard')


@login_required
def paiements_retard_view(request):
    today = timezone.localdate()
    _marquer_paiements_en_retard()
    paiements = list(
        Paiement.objects.filter(statut='En retard', date_echeance__lt=today)
        .select_related('contrat__locataire', 'contrat__propriete')
        .order_by('date_echeance', 'pk')
    )
    for paiement in paiements:
        paiement.jours_retard = (today - paiement.date_echeance).days
    return render(request, 'core/paiements_retard.html', {'paiements': paiements})


@login_required
@require_POST
def paiement_marquer_rappel_view(request, pk):
    paiement = get_object_or_404(
        Paiement,
        pk=pk,
        statut='En retard',
        date_echeance__lt=timezone.localdate(),
    )
    if not paiement.rappel_envoye:
        paiement.rappel_envoye = True
        paiement.date_rappel = timezone.now()
        paiement.save(update_fields=['rappel_envoye', 'date_rappel'])
    if request.headers.get('HX-Request') == 'true':
        paiement = Paiement.objects.select_related(
            'contrat__locataire', 'contrat__propriete',
        ).get(pk=paiement.pk)
        paiement.jours_retard = (timezone.localdate() - paiement.date_echeance).days
        return render(request, 'core/_paiement_retard_row.html', {'paiement': paiement})
    return redirect('paiements_retard')


@login_required
def paiement_create_view(request):
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save()
            if paiement.statut == 'Payé':
                return redirect('paiement_receipt', pk=paiement.pk)
            return redirect('paiements_list')
    else:
        form = PaiementForm(initial={'date_echeance': timezone.localdate()})
    return render(request, 'core/paiement_form.html', {'form': form})


@login_required
def paiement_receipt_view(request, pk):
    paiement = get_object_or_404(
        Paiement.objects.select_related('contrat__locataire', 'contrat__propriete'),
        pk=pk,
        statut='Payé',
    )
    return render(request, 'core/paiement_receipt.html', {'paiement': paiement})


@login_required
def preferences_view(request):
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('preferences')
    else:
        form = UserPreferenceForm(instance=preferences)
    return render(request, 'core/preferences.html', {'form': form})
