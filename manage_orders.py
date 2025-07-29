#!/usr/bin/env python
"""
Script utilitaire pour gérer les commandes de test dans l'application e-commerce.

Ce script permet de :
- Créer des commandes de test
- Afficher les commandes existantes
- Modifier le statut des commandes
"""
import os
import sys
import random
from datetime import datetime, timedelta
from django.utils import timezone

def setup_django():
    """Configure les paramètres Django pour pouvoir utiliser les modèles."""
    import django
    from django.conf import settings
    
    # Configure Django
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'accounts',
                'catalog',
                'orders',
            ],
            AUTH_USER_MODEL='accounts.CustomUser',
            ROOT_URLCONF='ecommerce.urls',
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [os.path.join(BASE_DIR, 'templates')],
                    'APP_DIRS': True,
                },
            ],
            USE_TZ=True,
            TIME_ZONE='UTC',
        )
        django.setup()

def create_test_orders(count=5):
    """Crée des commandes de test pour les utilisateurs existants."""
    from django.contrib.auth import get_user_model
    from catalog.models import Produit
    from orders.models import Commande, LigneCommande
    
    User = get_user_model()
    
    # Vérifier qu'il y a des utilisateurs et des produits
    users = list(User.objects.all())
    produits = list(Produit.objects.all())
    
    if not users or not produits:
        print("Erreur: Vous devez d'abord créer des utilisateurs et des produits.")
        return
    
    # Créer des commandes de test
    for i in range(count):
        # Choisir un utilisateur aléatoire
        user = random.choice(users)
        
        # Créer une commande
        commande = Commande.objects.create(
            utilisateur=user,
            adresse_livraison=f"{random.randint(1, 200)} Rue de l'Exemple",
            code_postal=f"{random.randint(10000, 95999)}",
            ville=random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux"]),
            pays="France",
            montant_total=0,  # Sera mis à jour après l'ajout des lignes
            paye=random.choice([True, False])
        )
        
        # Ajouter entre 1 et 5 produits à la commande
        nb_produits = random.randint(1, min(5, len(produits)))
        produits_commande = random.sample(produits, nb_produits)
        
        total_commande = 0
        for produit in produits_commande:
            quantite = random.randint(1, 5)
            prix_unitaire = float(produit.prix)
            total_ligne = quantite * prix_unitaire
            total_commande += total_ligne
            
            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire
            )
        
        # Mettre à jour le montant total de la commande
        commande.montant_total = total_commande
        commande.save()
        
        # Définir une date de commande aléatoire dans les 30 derniers jours
        jours_aleatoires = random.randint(0, 30)
        date_commande = timezone.now() - timedelta(days=jours_aleatoires)
        Commande.objects.filter(id=commande.id).update(date_commande=date_commande)
        
        # Changer aléatoirement le statut de certaines commandes
        if random.random() < 0.3:  # 30% de chance d'être livré
            commande.marquer_comme_livre()
        elif random.random() < 0.2:  # 20% de chance d'être annulé
            commande.annuler()
        
        print(f"Commande #{commande.id} créée pour {user.email}")

def list_orders():
    """Affiche la liste des commandes existantes."""
    from orders.models import Commande
    
    print("\n=== LISTE DES COMMANDES ===")
    print(f"{'ID':<5} {'Date':<20} {'Utilisateur':<30} {'Statut':<20} {'Montant':>10}")
    print("-" * 90)
    
    for cmd in Commande.objects.select_related('utilisateur').order_by('-date_commande'):
        print(f"{cmd.id:<5} {cmd.date_commande.strftime('%d/%m/%Y %H:%M'):<20} "
              f"{cmd.utilisateur.email[:28]:<30} {cmd.get_statut_display():<20} "
              f"{cmd.montant_total:>8.2f} €")

def update_order_status(order_id, new_status):
    """Met à jour le statut d'une commande."""
    from orders.models import Commande
    
    try:
        commande = Commande.objects.get(id=order_id)
        ancien_statut = commande.get_statut_display()
        
        if new_status.lower() == 'livre':
            if commande.marquer_comme_livre():
                print(f"Commande #{commande.id} marquée comme livrée (était: {ancien_statut})")
            else:
                print(f"Impossible de marquer la commande #{commande.id} comme livrée (statut actuel: {ancien_statut})")
        elif new_status.lower() == 'annule':
            if commande.annuler():
                print(f"Commande #{commande.id} annulée (était: {ancien_statut})")
            else:
                print(f"Impossible d'annuler la commande #{commande.id} (statut actuel: {ancien_statut})")
        else:
            print("Statut invalide. Utilisez 'livre' ou 'annule'.")
    except Commande.DoesNotExist:
        print(f"Erreur: Aucune commande avec l'ID {order_id} trouvée.")

def show_help():
    """Affiche l'aide pour l'utilisation du script."""
    print("""
Gestion des commandes - Script d'administration

Utilisation:
  python manage_orders.py [commande] [arguments]

Commandes disponibles:
  create [nombre]    Crée le nombre spécifié de commandes de test (par défaut: 5)
  list              Affiche la liste des commandes existantes
  update ID STATUT   Met à jour le statut d'une commande (STATUT: 'livre' ou 'annule')
  help              Affiche ce message d'aide

Exemples:
  python manage_orders.py create 10
  python manage_orders.py list
  python manage_orders.py update 5 livre
""")

if __name__ == "__main__":
    # Configurer Django
    setup_django()
    
    # Traiter les arguments de la ligne de commande
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        create_test_orders(count)
    elif command == 'list':
        list_orders()
    elif command == 'update' and len(sys.argv) == 4:
        order_id = int(sys.argv[2])
        new_status = sys.argv[3]
        update_order_status(order_id, new_status)
    elif command in ('help', '--help', '-h'):
        show_help()
    else:
        print("Commande non reconnue. Utilisez 'help' pour voir les commandes disponibles.")
        sys.exit(1)
