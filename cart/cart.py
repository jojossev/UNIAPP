from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from catalog.models import Produit


class Cart:
    """
    Classe qui gère le panier d'achat en utilisant la session Django.
    """
    
    def __init__(self, request):
        """
        Initialise le panier.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sauvegarder un panier vide dans la session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, produit, quantite=1, override_quantite=False):
        """
        Ajoute un produit au panier ou met à jour sa quantité.
        """
        produit_id = str(produit.id)
        if produit_id not in self.cart:
            self.cart[produit_id] = {'quantite': 0, 'prix': str(produit.prix)}
        
        if override_quantite:
            self.cart[produit_id]['quantite'] = quantite
        else:
            self.cart[produit_id]['quantite'] += quantite
        
        self.save()
    
    def save(self):
        """
        Marque la session comme modifiée pour s'assurer qu'elle est sauvegardée.
        """
        self.session.modified = True
    
    def remove(self, produit):
        """
        Supprime un produit du panier.
        """
        produit_id = str(produit.id)
        if produit_id in self.cart:
            del self.cart[produit_id]
            self.save()
    
    def __iter__(self):
        """
        Parcourt les articles du panier et récupère les produits depuis la base de données.
        """
        produits_ids = self.cart.keys()
        # Récupère les objets produits et les ajoute au panier
        produits = Produit.objects.filter(id__in=produits_ids)
        
        cart = self.cart.copy()
        for produit in produits:
            cart[str(produit.id)]['produit'] = produit
        
        for item in cart.values():
            item['prix'] = Decimal(item['prix'])
            item['prix_total'] = item['prix'] * item['quantite']
            yield item
    
    def __len__(self):
        """
        Compte tous les articles dans le panier.
        """
        return sum(item['quantite'] for item in self.cart.values())
    
    def get_total_prix(self):
        """
        Calcule le coût total des articles dans le panier.
        """
        return sum(
            Decimal(item['prix']) * item['quantite'] 
            for item in self.cart.values()
        )
    
    def clear(self):
        """
        Supprime le panier de la session.
        """
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()
