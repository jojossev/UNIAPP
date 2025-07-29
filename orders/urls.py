from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Historique des commandes de l'utilisateur connecté
    path('historique/', views.historique_commandes, name='historique'),
    
    # Détail d'une commande spécifique
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    
    # Annulation d'une commande par l'utilisateur
    path('commande/<int:commande_id>/annuler/', views.annuler_commande, name='annuler_commande'),
]
