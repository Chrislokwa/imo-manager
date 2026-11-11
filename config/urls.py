"""
URL configuration for Imo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core.views import (
    dashboard_view, 
    biens_list_view, 
    bien_detail_view,
    bien_create_view, 
    bien_update_view, 
    bien_delete_view,
    locataires_list_view,
    locataire_create_view,
    locataire_detail_view,
    contrat_create_view,
    paiements_list_view,
    paiement_create_view,
    paiement_receipt_view,
    paiements_retard_view,
    paiement_marquer_rappel_view,
    preferences_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard_view, name='dashboard'),
    path('biens/', biens_list_view, name='biens_list'),
    path('biens/<int:pk>/', bien_detail_view, name='bien_detail'),
    path('biens/ajouter/', bien_create_view, name='bien_create'),
    path('biens/<int:pk>/modifier/', bien_update_view, name='bien_update'),
    path('biens/<int:pk>/supprimer/', bien_delete_view, name='bien_delete'),
    path('locataires/', locataires_list_view, name='locataires_list'),
    path('locataires/ajouter/', locataire_create_view, name='locataire_create'),
    path('locataires/<int:pk>/', locataire_detail_view, name='locataire_detail'),
    path('contrats/ajouter/', contrat_create_view, name='contrat_create'),
    path('biens/<int:propriete_pk>/contrats/ajouter/', contrat_create_view, name='contrat_create_for_bien'),
    path('paiements/', paiements_list_view, name='paiements_list'),
    path('paiements/ajouter/', paiement_create_view, name='paiement_create'),
    path('paiements/retards/', paiements_retard_view, name='paiements_retard'),
    path('paiements/<int:pk>/rappel/', paiement_marquer_rappel_view, name='paiement_marquer_rappel'),
    path('paiements/<int:pk>/recu/', paiement_receipt_view, name='paiement_receipt'),
    path('parametres/', preferences_view, name='preferences'),
]
