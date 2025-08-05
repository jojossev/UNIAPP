"""
Module de gestion des suggestions basées sur l'historique utilisateur
"""
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, Q
from django.urls import reverse
from catalog.models import Produit, ImageProduit

logger = logging.getLogger(__name__)

def suggest_from_history(user_id, history):
    """
    Génère des suggestions basées sur l'historique utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
        history (list): Historique des produits consultés
        
    Returns:
        list: Suggestions basées sur l'historique
    """
    try:
        if not history:
            return []
            
        # Récupérer les catégories des produits de l'historique
        categories = set()
        for item in history:
            if 'categorie' in item and item['categorie']:
                categories.add(item['categorie'])
        
        # Si on a des catégories, chercher des produits similaires
        if categories:
            suggestions = Produit.objects.filter(
                Q(categorie__nom__in=categories) | 
                Q(categorie__parent__nom__in=categories),
                est_actif=True,
                en_stock=True
            ).distinct()[:5]
            
            return [{
                'id': p.id,
                'title': p.nom,
                'price': f"{p.prix:.2f}",
                'image_url': p.images.filter(est_principale=True).first().image.url if p.images.exists() else 
                            'https://via.placeholder.com/300x200?text=Image+non+disponible',
                'url': reverse('catalog:detail', kwargs={'pk': p.id, 'slug': p.slug})
            } for p in suggestions]
            
        return []
        
    except Exception as e:
        logger.error(f"Erreur dans suggest_from_history: {str(e)}", exc_info=True)
        return []

def get_suggestions(user_id=None, limit=5):
    """
    Récupère des suggestions de produits personnalisées.
    
    Args:
        user_id (int, optional): ID de l'utilisateur
        limit (int): Nombre maximum de suggestions à retourner
        
    Returns:
        list: Liste de dictionnaires contenant les suggestions de produits
    """
    try:
        # 1. D'abord essayer de récupérer des suggestions basées sur l'historique
        if user_id:
            # Ici, on pourrait récupérer l'historique réel de l'utilisateur
            # Pour l'instant, on utilise une liste vide
            user_history = []
            suggestions = suggest_from_history(user_id, user_history)
            
            # Si on a des suggestions, on les retourne
            if suggestions:
                return suggestions[:limit]
        
        # 2. Si pas d'historique ou pas d'utilisateur, retourner les meilleurs produits
        produits = Produit.objects.filter(
            est_actif=True,
            en_stock=True
        ).prefetch_related(
            Prefetch('images', queryset=ImageProduit.objects.filter(est_principale=True))
        ).order_by('-note_moyenne', '?')[:limit]
        
        # Construire la liste des suggestions
        suggestions = []
        for produit in produits:
            try:
                # Obtenir l'URL de l'image principale
                image_url = None
                if hasattr(produit, 'images') and produit.images.exists():
                    main_image = produit.images.first()
                    if main_image and hasattr(main_image, 'image') and hasattr(main_image.image, 'url'):
                        image_url = main_image.image.url
                
                # Si aucune image valide n'est trouvée
                if not image_url:
                    image_url = 'https://via.placeholder.com/300x200?text=Image+non+disponible'
                
                # Construire l'URL du produit
                try:
                    product_url = reverse('catalog:detail', kwargs={
                        'pk': produit.id,
                        'slug': produit.slug or 'produit'
                    })
                except:
                    product_url = f'/catalogue/produit/{produit.id}/'
                
                # Ajouter la suggestion
                suggestions.append({
                    "id": produit.id,
                    "title": produit.nom,
                    "price": f"{float(produit.prix):.2f}" if produit.prix is not None else "0.00",
                    "image_url": image_url,
                    "url": product_url
                })
                
            except (AttributeError, ObjectDoesNotExist) as e:
                logger.warning(f"Erreur avec le produit {getattr(produit, 'id', 'inconnu')}: {str(e)}")
                continue
        
        # Si on a des suggestions, les retourner
        if suggestions:
            return suggestions
            
        # Si aucune suggestion n'est disponible, retourner une suggestion par défaut
        return [{
            "id": 0,
            "title": "Découvrez nos produits",
            "price": "0.00",
            "image_url": "https://via.placeholder.com/300x200?text=Découvrir+nos+produits",
            "url": "/catalogue/"
        }]
        
    except Exception as e:
        logger.error(f"Erreur critique dans get_suggestions: {str(e)}", exc_info=True)
        
        # En cas d'erreur critique, retourner une suggestion d'erreur
        return [{
            "id": 0,
            "title": "Découvrez nos produits",
            "price": "0.00",
            "image_url": "https://via.placeholder.com/300x200?text=Découvrir+nos+produits",
            "url": "/catalogue/"
        }]
