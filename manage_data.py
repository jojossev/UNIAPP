import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import django
from django.utils.text import slugify

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from catalog.models import Categorie, Produit, ImageProduit, AvisProduit, CaracteristiqueProduit
from orders.models import Commande, LigneCommande

# Récupération du modèle utilisateur personnalisé
User = get_user_model()

def create_test_data():
    """Fonction principale pour créer des données de test."""
    print("Début de la création des données de test...")
    
    # Création d'un utilisateur admin s'il n'existe pas
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='Système',
            role='admin'
        )
        print("Utilisateur admin créé avec succès!")
    
    # Données de test pour les catégories
    categories_data = [
        'Électronique', 'Informatique', 'Téléphonie', 'Mode', 'Maison', 
        'Jardin', 'Beauté', 'Santé', 'Sport', 'Loisirs', 'Jouets', 'Bébé',
        'Auto-Moto', 'Bricolage', 'Cuisine', 'Électroménager', 'High-Tech',
        'Jeux vidéo', 'Livres', 'Musique', 'Instruments de musique', 'Bien-être',
        'Épicerie', 'Vins et spiritueux', 'Bureau', 'Fournitures scolaires',
        'Animalerie', 'Montres et bijoux', 'Bagagerie', 'Chaussures'
    ]
    
    # Création des catégories
    categories = []
    for nom in categories_data:
        categorie, created = Categorie.objects.get_or_create(
            nom=nom,
            defaults={
                'description': f'Description pour la catégorie {nom}',
                'est_active': True
            }
        )
        if created:
            print(f"Catégorie créée : {nom}")
        categories.append(categorie)
    
    # Données de test pour les produits
    produits_data = [
        # Électronique
        {"nom": "Smartphone X", "prix": 899.99, "categorie": "Téléphonie"},
        {"nom": "Écouteurs sans fil", "prix": 149.99, "categorie": "Électronique"},
        {"nom": "Montre connectée", "prix": 249.99, "categorie": "Électronique"},
        
        # Informatique
        {"nom": "Ordinateur portable", "prix": 1299.99, "categorie": "Informatique"},
        {"nom": "Souris sans fil", "prix": 49.99, "categorie": "Informatique"},
        
        # Mode
        {"nom": "Jean slim", "prix": 59.99, "categorie": "Mode"},
        {"nom": "Veste en cuir", "prix": 199.99, "categorie": "Mode"},
        
        # Maison
        {"nom": "Tapis moderne", "prix": 129.99, "categorie": "Maison"},
        
        # Jardin
        {"nom": "Tondeuse à gazon", "prix": 249.99, "categorie": "Jardin"},
        
        # Ajoutez plus de produits selon vos besoins
    ]
    
    # Création des produits
    produits = []
    for i, prod_data in enumerate(produits_data, 1):
        # Trouver la catégorie correspondante
        categorie = Categorie.objects.get(nom=prod_data['categorie'])
        
        # Créer le produit
        produit = Produit(
            reference=f"REF-{1000 + i}",
            nom=prod_data['nom'],
            description=f"Description détaillée pour {prod_data['nom']}",
            resume=f"Résumé pour {prod_data['nom']}",
            prix=Decimal(str(prod_data['prix'])),
            categorie=categorie,
            quantite=random.randint(5, 100),
            est_actif=True,
            est_nouveau=random.choice([True, False]),
            est_meilleur_vente=random.choice([True, False]),
            meta_titre=f"{prod_data['nom']} | Mon E-commerce"  # Valeur par défaut si SITE_NAME n'est pas défini
        )
        
        # Sauvegarder le produit
        produit.save()
        
        # Ajouter un prix promotionnel aléatoire (dans 30% des cas)
        if random.random() < 0.3:
            produit.prix_promotionnel = Decimal(prod_data['prix'] * 0.8)  # 20% de réduction
            produit.save()
        
        produits.append(produit)
        print(f"Produit créé : {produit.nom}")
    
    # Création de quelques commandes de test
    statuts = [Commande.STATUT_EN_COURS, Commande.STATUT_LIVRE, Commande.STATUT_ANNULE]
    
    for i in range(1, 31):  # 30 commandes
        # Choisir un statut aléatoire
        statut = random.choice(statuts)
        
        # Créer la commande
        commande = Commande.objects.create(
            utilisateur=admin_user,
            statut=statut,
            adresse_livraison=f"{random.randint(1, 200)} Rue des Exemples",
            code_postal=f"{75000 + random.randint(1, 20)}",
            ville="Paris",
            pays="France",
            montant_total=0,  # Mise à jour après création des lignes
            paye=random.choice([True, False])
        )
        
        # Ajouter des lignes de commande
        total_commande = Decimal('0.00')
        nb_lignes = random.randint(1, 5)  # 1 à 5 articles par commande
        
        for _ in range(nb_lignes):
            produit = random.choice(produits)
            quantite = random.randint(1, 3)
            prix_unitaire = produit.prix_promotionnel or produit.prix
            total_ligne = prix_unitaire * quantite
            
            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire
            )
            
            total_commande += total_ligne
        
        # Mettre à jour le montant total de la commande
        commande.montant_total = total_commande
        commande.save()
        
        print(f"Commande #{commande.id} créée avec {nb_lignes} articles")
    
    print("\nDonnées de test créées avec succès!")

if __name__ == "__main__":
    create_test_data()
