"""
Module de recommandation de produits personnalisée
"""
import random
from django.conf import settings
from django.db.models import Count, Avg
from catalog.models import Produit, Categorie

def get_recommendations(user_id=None, history=None, top_n=6):
    """
    Retourne une liste de recommandations de produits basée sur l'historique de l'utilisateur
    ou des produits populaires si l'utilisateur est anonyme.
    
    Args:
        user_id (int, optional): ID de l'utilisateur connecté
        history (list, optional): Historique des produits consultés
        top_n (int): Nombre de recommandations à retourner
        
    Returns:
        list: Liste de dictionnaires contenant les informations des produits recommandés
    """
    try:
        # Récupérer les produits en stock avec leurs images
        produits_disponibles = Produit.objects.filter(
            stock__gt=0  # Uniquement les produits en stock
        ).select_related('categorie').prefetch_related('images')
        
        # Si l'utilisateur est connecté, on peut personnaliser les recommandations
        if user_id and history:
            # Ici, on pourrait implémenter une logique de recommandation personnalisée
            # basée sur l'historique de navigation/achat de l'utilisateur
            # Pour l'instant, on sélectionne des produits aléatoires
            produits_recommandes = list(produits_disponibles.order_by('?')[:top_n])
        else:
            # Pour les utilisateurs anonymes, on retourne les produits les mieux notés
            produits_recommandes = list(produits_disponibles.annotate(
                avg_rating=Avg('commentaires__note')
            ).order_by('-avg_rating', '?')[:top_n])
        
        # Formater les résultats pour le template
        recommendations = []
        for produit in produits_recommandes:
            # Récupérer l'image principale du produit ou une image par défaut
            image_url = None
            if produit.images.exists():
                image_url = produit.images.first().image.url
            else:
                image_url = f"https://via.placeholder.com/300x200?text={produit.nom[:20]}"
            
            # Construire l'URL du produit
            produit_url = f"/catalogue/produit/{produit.id}/"
            
            recommendations.append({
                'id': produit.id,
                'nom': produit.nom,
                'description': produit.description[:100] + '...' if produit.description else '',
                'prix': float(produit.prix),
                'categorie': produit.categorie.nom if produit.categorie else '',
                'url': produit_url,
                'image': image_url,
                'stock': produit.stock,
                'note_moyenne': float(produit.moyenne_notes() or 0)
            })
        
        return recommendations
        
    except Exception as e:
        # En cas d'erreur, retourner une liste vide
        print(f"Erreur dans get_recommendations: {str(e)}")
        return []
